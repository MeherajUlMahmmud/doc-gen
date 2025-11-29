import logging
import time
from functools import wraps

from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from common.api_response import ApiResponse

logger = logging.getLogger(__name__)


def api_rate_limit(requests=5, window=60, key_prefix='api', use_email=True):
    """
    Rate limiter for Django API views, supporting IP and email-based limiting.
    Returns a 429 ApiResponse when limit is exceeded, using a sliding window approach.
    
    Uses Redis for rate limiting (via Django's cache backend configured in settings).

    Args:
        requests: Maximum number of requests allowed in the window
        window: Time window in seconds
        key_prefix: Prefix for cache key to differentiate endpoints
        use_email: If True, also rate limit by email from POST data or authenticated user

    Usage:
        @api_rate_limit(requests=5, window=60, use_email=True)
        def my_api_view(request):
            pass

        @method_decorator(api_rate_limit(requests=5, window=60, use_email=True), name='post')
        class MyAPIView(APIView):
            pass
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract request from args without binding signature
            # This handles both function views and class-based views
            request = None
            view_instance = None
            
            # Try to find request in the actual arguments
            if len(args) >= 1 and hasattr(args[0], 'META'):
                request = args[0]
            elif len(args) >= 2 and hasattr(args[1], 'META'):
                view_instance = args[0]
                request = args[1]

            if not request or not hasattr(request, 'META'):
                logger.warning(f"[APIRateLimit] Could not find request object for {func.__name__}")
                return func(*args, **kwargs)

            def get_client_ip(request):
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0].strip()
                else:
                    ip = request.META.get('REMOTE_ADDR', 'unknown')
                return ip

            ip = get_client_ip(request)
            if view_instance:
                view_name = f"{view_instance.__class__.__name__}_{func.__name__}"
            else:
                view_name = func.__name__

            endpoint = f"{request.method}_{request.path_info.replace('/', '_')}"
            ip_cache_key = f'rate_limit_{key_prefix}_{view_name}_{endpoint}_{ip}'

            try:
                current_time = time.time()

                # Handle email-based rate limiting
                if use_email:
                    email = None
                    if request.method == 'POST':
                        email = request.POST.get('email', '').strip()
                    elif request.user.is_authenticated:
                        email = getattr(request.user, 'email', '').strip()

                    if email:
                        email_cache_key = f'rate_limit_{key_prefix}_email_{view_name}_{endpoint}_{email}'
                        email_timestamps = cache.get(email_cache_key, [])

                        email_timestamps = [
                            ts for ts in email_timestamps
                            if current_time - ts <= window
                        ]

                        if len(email_timestamps) >= requests:
                            oldest_request = min(email_timestamps) if email_timestamps else current_time
                            wait_time = window - (current_time - oldest_request)
                            logger.warning(
                                f"[APIRateLimit] Email rate limit exceeded for {email_cache_key}, wait time: {wait_time:.2f}s")
                            return ApiResponse.error(
                                message=f'Too many requests from this email address. Please try again in {int(wait_time)} seconds.',
                                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                meta={'retry_after': int(wait_time)}
                            )

                        email_timestamps.append(current_time)
                        cache.set(email_cache_key, email_timestamps, window + 10)
                        logger.info(
                            f"[APIRateLimit] Email request {len(email_timestamps)}/{requests} for {email_cache_key}")

                # Handle IP-based rate limiting
                ip_timestamps = cache.get(ip_cache_key, [])

                ip_timestamps = [
                    ts for ts in ip_timestamps
                    if current_time - ts <= window
                ]

                if len(ip_timestamps) >= requests:
                    oldest_request = min(ip_timestamps) if ip_timestamps else current_time
                    wait_time = window - (current_time - oldest_request)
                    logger.warning(
                        f"[APIRateLimit] IP rate limit exceeded for {ip_cache_key}, wait time: {wait_time:.2f}s")
                    return ApiResponse.error(
                        message=f'Too many requests from this IP address. Please try again in {int(wait_time)} seconds.',
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        meta={'retry_after': int(wait_time)}
                    )

                ip_timestamps.append(current_time)
                cache.set(ip_cache_key, ip_timestamps, window + 10)
                logger.info(f"[APIRateLimit] IP request {len(ip_timestamps)}/{requests} for {ip_cache_key}")

            except Exception as e:
                logger.error(f"[APIRateLimit] Error in rate limiting for {ip_cache_key}: {str(e)}")
                pass

            return func(*args, **kwargs)

        return wrapper

    return decorator


def html_rate_limit(requests=10, window=60, key_prefix='html', use_email=True):
    """
    Rate limiter for Django HTML rendering views, supporting IP and email-based limiting.
    Redirects to a custom error page when limit is exceeded.
    
    Uses Redis for rate limiting (via Django's cache backend configured in settings).

    Args:
        requests: Maximum number of requests allowed in the window
        window: Time window in seconds
        key_prefix: Prefix for cache key to differentiate endpoints
        use_email: If True, also rate limit by email from POST data or authenticated user

    Usage:
        @html_rate_limit(requests=10, window=60, use_email=True)
        def my_view(request):
            pass

        @method_decorator(html_rate_limit(requests=10, window=60, use_email=True), name='get')
        class MyView(View):
            pass
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract request from args without binding signature
            # This handles both function views and class-based views
            request = None
            view_instance = None
            
            # Try to find request in the actual arguments
            if len(args) >= 1 and hasattr(args[0], 'META'):
                request = args[0]
            elif len(args) >= 2 and hasattr(args[1], 'META'):
                view_instance = args[0]
                request = args[1]

            if not request or not hasattr(request, 'META'):
                logger.warning(f"[HTMLRateLimit] Could not find request object for {func.__name__}")
                return func(*args, **kwargs)

            def get_client_ip(request):
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0].strip()
                else:
                    ip = request.META.get('REMOTE_ADDR', 'unknown')
                return ip

            ip = get_client_ip(request)
            if view_instance:
                view_name = f"{view_instance.__class__.__name__}_{func.__name__}"
            else:
                view_name = func.__name__

            endpoint = f"{request.method}_{request.path_info.replace('/', '_')}"
            ip_cache_key = f'rate_limit_{key_prefix}_{view_name}_{endpoint}_{ip}'

            try:
                current_time = time.time()

                # Handle email-based rate limiting
                if use_email:
                    email = None
                    if request.method == 'POST':
                        email = request.POST.get('email', '').strip()
                    elif request.user.is_authenticated:
                        email = getattr(request.user, 'email', '').strip()

                    if email:
                        email_cache_key = f'rate_limit_{key_prefix}_email_{view_name}_{endpoint}_{email}'
                        email_timestamps = cache.get(email_cache_key, [])

                        email_timestamps = [
                            ts for ts in email_timestamps
                            if current_time - ts <= window
                        ]

                        if len(email_timestamps) >= requests:
                            oldest_request = min(email_timestamps) if email_timestamps else current_time
                            wait_time = window - (current_time - oldest_request)
                            logger.warning(
                                f"[HTMLRateLimit] Email rate limit exceeded for {email_cache_key}, wait time: {wait_time:.2f}s")
                            return HttpResponseRedirect(reverse('rate_limit_error'))

                        email_timestamps.append(current_time)
                        cache.set(email_cache_key, email_timestamps, window + 10)
                        logger.info(
                            f"[HTMLRateLimit] Email request {len(email_timestamps)}/{requests} for {email_cache_key}")

                # Handle IP-based rate limiting
                ip_timestamps = cache.get(ip_cache_key, [])

                ip_timestamps = [
                    ts for ts in ip_timestamps
                    if current_time - ts <= window
                ]

                if len(ip_timestamps) >= requests:
                    oldest_request = min(ip_timestamps) if ip_timestamps else current_time
                    wait_time = window - (current_time - oldest_request)
                    logger.warning(
                        f"[HTMLRateLimit] IP rate limit exceeded for {ip_cache_key}, wait time: {wait_time:.2f}s")
                    return HttpResponseRedirect(reverse('rate_limit_error'))

                ip_timestamps.append(current_time)
                cache.set(ip_cache_key, ip_timestamps, window + 10)
                logger.info(f"[HTMLRateLimit] IP request {len(ip_timestamps)}/{requests} for {ip_cache_key}")

            except Exception as e:
                logger.error(f"[HTMLRateLimit] Error in rate limiting for {ip_cache_key}: {str(e)}")
                pass

            return func(*args, **kwargs)

        return wrapper

    return decorator
