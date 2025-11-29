import ipaddress
import logging
import re
import time
import uuid
from datetime import datetime
from threading import local, Thread
from typing import Optional, Set, Callable, Dict

from django.db import connection
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

from base import settings
from common.models import RequestLog, BlockedIPModel, IPTrackingModel

_local = local()
logger = logging.getLogger(__name__)


class CacheRequestBodyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Cache the body before anything else reads it
        if not hasattr(request, '_body'):
            try:
                request._body = request.body
            except Exception:
                request._body = None
        response = self.get_response(request)
        return response


class TraceIDMiddleware:
    """
    Middleware that adds a trace ID to each request for tracking through logs.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        trace_id = uuid.uuid4().hex
        request.trace_id = trace_id
        _local.trace_id = trace_id

        response = self.get_response(request)
        return response


class RequestLogMiddleware(MiddlewareMixin):
    """
    Middleware that logs all HTTP requests and responses.
    """

    EXCLUDED_PATHS = settings.REQUEST_LOG_EXCLUDED_PATHS
    EXCLUDED_PATTERNS = [re.compile(pattern) for pattern in EXCLUDED_PATHS]

    # Maximum content size to log (to prevent huge responses from being stored)
    MAX_CONTENT_SIZE = getattr(settings, 'REQUEST_LOG_MAX_CONTENT_SIZE', 10000)

    @staticmethod
    def process_request(request: HttpRequest) -> None:
        """Store the start time to calculate response time"""
        request.start_time = time.time()

    def should_skip_logging(self, request: HttpRequest) -> bool:
        """Determine if this request should be skipped for logging"""
        path = request.path.lower()
        return any(pattern.match(path) for pattern in self.EXCLUDED_PATTERNS)

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Process and log the response"""
        if self.should_skip_logging(request):
            return response

        response_time = time.time() - getattr(request, 'start_time', time.time())

        try:
            # Get trace ID from TraceIDMiddleware if available
            trace_id = getattr(request, 'trace_id', None)

            # Get request body, safely
            body = getattr(request, '_body', None)
            request_body = self._get_safe_content(
                body.decode('utf-8') if body else None
            )

            # Get user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Get response content safely with encoding error handling
            response_content = self._get_safe_content(
                self._safe_decode_response(response)
            )

            RequestLog.objects.create(
                user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                ip_address=self.get_client_ip(request),
                endpoint=request.path,
                method=request.method,
                request_body=request_body,
                status_code=response.status_code,
                response=response_content,
                user_agent=user_agent,
                trace_id=trace_id,
                response_time=response_time
            )
        except Exception as e:
            logger.error(f'Failed to create request log: {str(e)}', exc_info=True)

        return response

    def _safe_decode_response(self, response: HttpResponse) -> str:
        """Safely decode response content with proper error handling"""
        if not hasattr(response, 'content'):
            return str(response)

        try:
            # Try UTF-8 first
            return response.content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Try latin-1 as fallback (it can decode any byte sequence)
                return response.content.decode('latin-1')
            except UnicodeDecodeError:
                # If all else fails, use error replacement
                return response.content.decode('utf-8', errors='replace')

    def _get_safe_content(self, content: Optional[str]) -> Optional[str]:
        """Safely truncate content to prevent huge logs"""
        if not content:
            return None

        if len(content) > self.MAX_CONTENT_SIZE:
            return content[:self.MAX_CONTENT_SIZE] + "... [truncated]"
        return content

    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip


class IPBlockerMiddleware:
    """
    Django middleware to detect and block IPs that attempt to access sensitive files
    like .env or .git files/directories. Blocked IPs are stored in a database model.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

        # Load configuration from settings
        self.max_attempts = int(getattr(settings, 'IP_BLOCK_MAX_ATTEMPTS', 3))
        self.whitelisted_ips = getattr(settings, 'IP_WHITELIST', [])
        self.enabled = getattr(settings, 'IP_BLOCKER_ENABLED', True)

        # Convert string IPs to proper IP objects for comparison
        self.whitelist = [ipaddress.ip_network(
            ip) for ip in self.whitelisted_ips if ip]

        # Load patterns from settings or use defaults
        patterns = getattr(settings, 'IP_BLOCK_PATTERNS', [])

        # Compile regex patterns with flags for better performance
        self.compiled_patterns = [re.compile(
            pattern, re.IGNORECASE) for pattern in patterns]

        # Initialize cache for blocked IPs
        self.blocked_ips_cache: Set[str] = set()

        # Try to refresh the cache, but handle database configuration errors gracefully
        try:
            self._refresh_blocked_ips_cache()
        except Exception as e:
            # Log the error but don't crash during initialization
            logger.warning(f"Error initializing blocked IPs cache: {str(e)}")
            # We'll try again later when the database is properly configured

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Skip if middleware is disabled
        if not self.enabled:
            return self.get_response(request)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Check if IP is whitelisted
        if self._is_ip_whitelisted(client_ip):
            return self.get_response(request)

        # Check if IP is already blocked (using cache)
        if self._is_ip_blocked(client_ip):
            return HttpResponseForbidden(b"Access denied. Your IP has been blocked.")

        # Check if the request path matches any sensitive patterns
        path = request.path.lower()
        matched_pattern = self._check_path_for_patterns(path)

        if matched_pattern:
            self._record_attempt(client_ip, matched_pattern)
            blocked_ip = self._get_blocked_ip(client_ip)

            if blocked_ip and blocked_ip.attempts >= self.max_attempts:
                if not blocked_ip.is_active:
                    self._block_ip(blocked_ip)
                    # Update the cache
                    self._refresh_blocked_ips_cache()
                return HttpResponseForbidden(b"Access denied. Your IP has been blocked.")

            return HttpResponseForbidden(b"Access denied. Suspicious activity detected.")

        # No sensitive pattern found, continue with the request
        return self.get_response(request)

    def _check_path_for_patterns(self, path: str) -> Optional[str]:
        """Check if path matches any sensitive patterns and return the matched pattern"""
        for pattern in self.compiled_patterns:
            if pattern.search(path):
                return pattern.pattern
        return None

    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip

    def _is_ip_whitelisted(self, ip: str) -> bool:
        """Check if IP is in whitelist"""
        if not ip:
            return False

        try:
            client_ip = ipaddress.ip_address(ip)
            return any(client_ip in white_ip for white_ip in self.whitelist)
        except ValueError:
            logger.warning(f"Invalid IP format: {ip}")
            return False

    def _is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked (cached)"""
        return ip in self.blocked_ips_cache

    def _refresh_blocked_ips_cache(self) -> None:
        """Refresh the cache of blocked IPs"""
        try:
            # Import here to avoid circular imports
            from common.models import BlockedIPModel

            # Check if database is properly configured
            if not hasattr(settings, 'DATABASES') or 'default' not in settings.DATABASES:
                logger.warning("Database settings not found, skipping blocked IPs refresh")
                return

            # Check if database is properly configured before querying
            if 'ENGINE' not in settings.DATABASES.get('default', {}):
                logger.warning("Database not properly configured yet, skipping blocked IPs refresh")
                return

            self.blocked_ips_cache = set(
                BlockedIPModel.objects.filter(
                    is_active=True).values_list('ip_address', flat=True)
            )
        except Exception as e:
            logger.warning(f"Error refreshing blocked IPs cache: {str(e)}")
            self.blocked_ips_cache = set()

    @staticmethod
    def _get_blocked_ip(ip: str) -> Optional[BlockedIPModel]:
        """Get the BlockedIPModel record for an IP if it exists"""
        try:
            return BlockedIPModel.objects.get(ip_address=ip)
        except BlockedIPModel.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error retrieving blocked IP {ip}: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def _record_attempt(ip: str, pattern_matched: Optional[str] = None) -> Optional[BlockedIPModel]:
        """Record a suspicious access attempt for an IP"""
        reason = f"Attempting to access {pattern_matched}" if pattern_matched else "Sensitive file access attempt"

        try:
            blocked_ip, created = BlockedIPModel.objects.get_or_create(
                ip_address=ip,
                defaults={
                    'reason': reason,
                    'attempts': 1,
                    'is_active': False,  # Not blocked yet, just tracking
                }
            )

            if not created:
                blocked_ip.attempts += 1
                blocked_ip.last_attempt = datetime.now()
                blocked_ip.save(update_fields=['attempts', 'last_attempt'])

            return blocked_ip
        except Exception as e:
            logger.error(f"Error recording IP block attempt for {ip}: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def _block_ip(blocked_ip: BlockedIPModel) -> None:
        """Block an IP address"""
        try:
            blocked_ip.is_active = True
            blocked_ip.created_at = datetime.now()
            blocked_ip.save(update_fields=['is_active', 'created_at'])
        except Exception as e:
            logger.error(f"Error blocking IP {blocked_ip.ip_address}: {str(e)}", exc_info=True)


class IPTrackingMiddleware:
    """
    Middleware that tracks IP addresses and determines location for all API requests
    except admin APIs. This middleware runs the same logic as in the login view
    for all API endpoints and saves the data to the database.
    """
    EXCLUDED_PATHS = getattr(settings, 'REQUEST_LOG_EXCLUDED_PATHS',
                             [r'^/admin', r'^/favicon\.ico', r'^/static'])

    # Compile excluded paths for faster matching
    EXCLUDED_PATTERNS = [re.compile(pattern) for pattern in EXCLUDED_PATHS]

    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.enabled = getattr(settings, 'IP_TRACKING_ENABLED', True)

        # Test database connection during initialization
        try:
            connection.ensure_connection()
        except Exception as e:
            logger.error(f"IPTrackingMiddleware initialization failed: {str(e)}")

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Skip if middleware is disabled
        if not self.enabled:
            return self.get_response(request)

        path = request.path.lower()
        if any(pattern.match(path) for pattern in self.EXCLUDED_PATTERNS):
            return self.get_response(request)

        # Set start time for response time calculation
        request.start_time = time.time()

        # Track IP with timeout
        tracking_thread = Thread(target=self._track_ip_and_location, args=(request,))
        tracking_thread.daemon = True
        tracking_thread.start()

        # Wait for tracking to complete with 500ms timeout
        tracking_thread.join(timeout=0.5)

        if tracking_thread.is_alive():
            logger.warning(f'IP tracking timed out for {path}, skipping...')

        response = self.get_response(request)

        # Save IP tracking data to database after response
        if hasattr(request, 'ip_address'):
            try:
                self._save_ip_tracking_data(request, response)
            except Exception as e:
                logger.error(f'Failed to save IP tracking data for {path}: {str(e)}', exc_info=True)

        return response

    def _track_ip_and_location(self, request: HttpRequest) -> None:
        """
        Track IP address and determine location for the request.
        This method contains the same logic as in the LoginAPIView.
        """
        try:
            # Get the IP address and user agent
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            device_info = self._parse_user_agent(user_agent)

            # Determine user's location
            ip_info = self._retrieve_ip_information(ip_address)

            country, country_code, continent, continent_code = self._get_country_from_ip_info(ip_info)
            location = country if country else "Unknown location"

            # Store the information in request for potential use in views
            request.ip_address = ip_address
            request.user_agent = user_agent
            request.device_info = device_info
            request.ip_info = ip_info
            request.location = location
            request.country = country
            request.country_code = country_code
            request.continent = continent
            request.continent_code = continent_code

        except Exception as e:
            logger.error(f'Error tracking IP and location: {str(e)}', exc_info=True)
            raise

    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')

        return ip

    @staticmethod
    def _parse_user_agent(user_agent_string: str) -> Dict[str, str]:
        """
        Parse user agent string to get device information.
        """
        try:
            from user_agents import parse
            user_agent = parse(user_agent_string)
            device_info = {
                'device': user_agent.device.family,
                'browser': user_agent.browser.family,
                'os': user_agent.os.family
            }
            return device_info
        except Exception as e:
            logger.error(f'Error parsing user agent: {str(e)}')
            return {'device': 'Unknown', 'browser': 'Unknown', 'os': 'Unknown'}

    @staticmethod
    def _retrieve_ip_information(ip: str) -> Dict[str, str]:
        """
        Determine the country of origin for an IP address.
        """
        try:
            import requests

            if ip == '127.0.0.1' or ip == '0.0.0.0' or ip.startswith('192.168.') or ip.startswith('10.'):
                return {}

            ip_api_url: str = f"http://ip-api.com/json/{ip}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,currency,isp,org,as,mobile,query"

            response = requests.get(ip_api_url, timeout=0.4)  # 400ms timeout to allow time for processing

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return data
                else:
                    logger.warning(f'IP API failed for {ip}: {data.get("message", "Unknown error")}')
            else:
                logger.warning(f'IP API HTTP error for {ip}: {response.status_code}')

            return {}
        except requests.exceptions.Timeout:
            logger.error(f'Timeout getting IP info for {ip}')
            return {}
        except requests.exceptions.RequestException as e:
            logger.error(f'Request error getting IP info for {ip}: {str(e)}')
            return {}
        except Exception as e:
            logger.error(f'Error getting IP info for {ip}: {str(e)}')
            return {}

    @staticmethod
    def _get_country_from_ip_info(ip_info: Dict[str, str]) -> tuple[str, str, str, str]:
        """Extract country information from IP info dictionary"""
        country = ip_info.get('country', '')
        country_code = ip_info.get('countryCode', '')
        continent = ip_info.get('continent', '')
        continent_code = ip_info.get('continentCode', '')

        return country, country_code, continent, continent_code

    @staticmethod
    def _save_ip_tracking_data(request: HttpRequest, response: HttpResponse) -> None:
        """
        Save IP tracking data to the database.
        This method is called after the response is generated.
        """
        try:
            # Check database connection
            connection.ensure_connection()

            # Calculate response time
            response_time = None
            if hasattr(request, 'start_time'):
                response_time = time.time() - request.start_time

            # Get trace ID if available
            trace_id = getattr(request, 'trace_id', None)

            # Get user if authenticated
            user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user

            # Get IP address
            ip_address = getattr(request, 'ip_address', '')

            # Prepare data for creation
            tracking_data = {
                'user': user,
                'ip_address': ip_address,
                'endpoint': request.path,
                'method': request.method,
                'user_agent': getattr(request, 'user_agent', ''),

                # Device information
                'device_type': getattr(request, 'device_info', {}).get('device', ''),
                'browser': getattr(request, 'device_info', {}).get('browser', ''),
                'operating_system': getattr(request, 'device_info', {}).get('os', ''),

                # Location information
                'country': getattr(request, 'country', ''),
                'country_code': getattr(request, 'country_code', ''),
                'continent': getattr(request, 'continent', ''),
                'continent_code': getattr(request, 'continent_code', ''),
                'region': getattr(request, 'ip_info', {}).get('region', ''),
                'region_name': getattr(request, 'ip_info', {}).get('regionName', ''),
                'city': getattr(request, 'ip_info', {}).get('city', ''),
                'district': getattr(request, 'ip_info', {}).get('district', ''),
                'zip_code': getattr(request, 'ip_info', {}).get('zip', ''),

                # Geographic coordinates
                'latitude': getattr(request, 'ip_info', {}).get('lat'),
                'longitude': getattr(request, 'ip_info', {}).get('lon'),

                # Additional information
                'timezone': getattr(request, 'ip_info', {}).get('timezone', ''),
                'currency': getattr(request, 'ip_info', {}).get('currency', ''),
                'isp': getattr(request, 'ip_info', {}).get('isp', ''),
                'organization': getattr(request, 'ip_info', {}).get('org', ''),
                'as_number': getattr(request, 'ip_info', {}).get('as', ''),
                'is_mobile': getattr(request, 'ip_info', {}).get('mobile'),

                # Request tracking
                'trace_id': trace_id,
                'status_code': response.status_code,
                'response_time': response_time,
            }

            # Create IP tracking record
            tracking_record = IPTrackingModel.objects.create(**tracking_data)

        except Exception as e:
            logger.error(f'Error saving IP tracking data for {request.path}: {str(e)}', exc_info=True)

            # Try to get more specific error information
            if hasattr(e, '__cause__') and e.__cause__:
                logger.error(f'Root cause: {str(e.__cause__)}')

            raise


class CacheControlMiddleware:
    """
    Middleware that adds appropriate cache headers to responses.
    This helps improve performance by enabling efficient caching.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Only add cache headers if not already set
        if 'Cache-Control' not in response:
            cache_control = self._get_cache_control_for_path(request.path, response.status_code)
            if cache_control:
                response['Cache-Control'] = cache_control

        return response

    def _get_cache_control_for_path(self, path: str, status_code: int) -> str:
        """
        Determine the appropriate Cache-Control header based on the request path and status code.
        """
        path = path.lower()

        # Don't cache error responses
        if status_code >= 400:
            return 'no-cache, no-store, must-revalidate'

        # API endpoints - different cache strategies
        if path.startswith('/api/'):
            if any(pattern in path for pattern in ['/auth/', '/login/', '/logout/']):
                return 'no-cache, no-store, must-revalidate'
            elif any(pattern in path for pattern in ['/user/', '/profile/', '/dashboard/']):
                return 'private, max-age=300'  # 5 minutes for user-specific data
            else:
                return 'public, max-age=3600'  # 1 hour for public API data

        # Admin and portal areas - no cache
        if any(pattern in path for pattern in ['/admin/', '/portal/']):
            return 'no-cache, no-store, must-revalidate'

        # Static files are handled by WhiteNoise
        if path.startswith('/static/'):
            return None  # Let WhiteNoise handle it

        # Media files - cache for 1 month
        if path.startswith('/media/'):
            return 'public, max-age=2592000'

        # Public pages - cache for 1 hour
        if path in ['/', '/about/', '/services/', '/contact/', '/quote/']:
            return 'public, max-age=3600'

        # Default for other pages - cache for 15 minutes
        return 'public, max-age=900'


class XRobotsTagMiddleware:
    """
    Middleware that adds X-Robots-Tag header to all responses.
    This helps control how search engines crawl and index pages.
    The middleware intelligently sets the header based on the request path.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Determine the appropriate X-Robots-Tag value based on the request path
        robots_tag = self._get_robots_tag_for_path(request.path)
        response['X-Robots-Tag'] = robots_tag

        return response

    def _get_robots_tag_for_path(self, path: str) -> str:
        """
        Determine the appropriate X-Robots-Tag value based on the request path.
        """
        path = path.lower()

        # Portal and admin areas should not be indexed
        if any(pattern in path for pattern in ['/portal/', '/admin/', '/api/', '/auth/']):
            return 'noindex, nofollow'

        # Static files and media should not be indexed
        if any(pattern in path for pattern in ['/static/', '/media/', '/favicon.ico']):
            return 'noindex, nofollow'

        # Public pages should be indexed
        return 'index, follow'
