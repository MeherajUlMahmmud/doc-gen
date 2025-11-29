import logging
import os
import random
import re
import string
import uuid
from datetime import datetime
from typing import Any, List, Optional, Dict

import boto3
from botocore.exceptions import NoCredentialsError

from base import settings

logger = logging.getLogger(__name__)


class Utils:
    @staticmethod
    def format_time(time_str: str) -> str:
        """Format time string to a consistent format."""
        try:
            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S,%f')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return time_str

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def read_log_file(
            file_path: str,
            lines: int = 100,
            trace_id: Optional[str] = None,
            level: str = ''
    ) -> List[str]:
        """Read and format log files with optional filtering."""
        try:
            with open(file_path, 'r') as file:
                log_lines = file.readlines()
        except FileNotFoundError:
            return []

        # Reverse the log lines for descending order
        log_lines.reverse()

        # Filter by trace ID if provided
        if trace_id:
            log_lines = [line for line in log_lines if trace_id in line]

        # Filter by log level if provided
        if level and level.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            log_lines = [line for line in log_lines if f'{level}' in line]

        # Format the timestamps in the logs
        formatted_log_lines = []
        for line in log_lines:
            match = re.match(
                r'(\w+\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+(.*)', line)
            if match:
                timestamp, rest = match.groups()
                formatted_log_lines.append(
                    f"{Utils.format_time(timestamp)} {rest}")
            else:
                formatted_log_lines.append(line)

        return formatted_log_lines[:lines]

    @staticmethod
    def save_picture_to_folder(picture_file: Any, folder_name: str) -> Optional[str]:
        """
        Save picture to either local storage or S3 bucket based on configuration.

        Determines storage type from settings and delegates to appropriate method.

        Args:
            picture_file: File object to save (must have 'name' attribute and support chunks() method)
            folder_name: Name of the folder to save the picture in

        Returns:
            URL to the saved picture or None if storage type is not supported
        """

        storage_type = settings.STORAGE_TYPE
        logger.info(f"Saving file to {storage_type}")

        if storage_type == 'local':
            return Utils._save_local_picture(picture_file, folder_name)
        elif storage_type == 's3':
            return Utils._save_s3_picture(picture_file, folder_name)
        return None

    @staticmethod
    def _save_local_picture(picture_file: Any, folder_name: str) -> str:
        """Save picture to local storage."""
        folder_path = os.path.join(settings.MEDIA_ROOT, folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        final_file_name = Utils._generate_unique_filename(picture_file.name)
        file_path = os.path.join(folder_path, final_file_name)

        with open(file_path, 'wb') as destination:
            for chunk in picture_file.chunks():
                destination.write(chunk)

        server_url = settings.SERVER_URL
        file_url = f"{server_url}{file_path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL).replace('//', '/')}"

        return file_url

    @staticmethod
    def _save_s3_picture(picture_file: Any, folder_name: str) -> Optional[str]:
        """
        Save picture to AWS S3 bucket.

        Creates an S3 client using credentials from settings, generates a unique filename,
        and uploads the file to the configured S3 bucket.

        Args:
            picture_file: File object to save
            folder_name: Name of the folder to save the picture in

        Returns:
            URL to the saved picture in S3 or None if credentials are not available
        """
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )

            final_file_name = Utils._generate_unique_filename(picture_file.name)
            logger.info(f"final_file_name: {final_file_name}")
            s3_file_path = os.path.join(folder_name, final_file_name).replace('\\', '/')

            s3_client.upload_fileobj(
                picture_file,
                settings.AWS_BUCKET_NAME,
                s3_file_path,
            )

            s3_file_url = (
                f"https://{settings.AWS_BUCKET_NAME}."
                f"s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_file_path}"
            )
            logger.info(f"s3_file_url: {s3_file_url}")

            return s3_file_url
        except NoCredentialsError:
            logger.error("Credentials not available")
            return None
        except Exception as e:
            logger.error(f"Error occurred while saving file to s3: {e}")

    @staticmethod
    def _generate_unique_filename(original_filename: str) -> str:
        """Generate a unique filename."""
        file_name = original_filename.replace(' ', '_')
        extension = file_name.split('.')[-1]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_file_name = f"{file_name.split('.')[0]}_{uuid.uuid4()}_{timestamp}.{extension}"

        return final_file_name[-100:] if len(final_file_name) > 100 else final_file_name

    @staticmethod
    def generate_unique_code(length):
        """Generate a unique code of specified length."""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def get_ip_tracking_info(request) -> Dict[str, Any]:
        """
        Get IP tracking information from request object.
        This method should be called in views to access the IP tracking data
        that was collected by the IPTrackingMiddleware.

        Args:
            request: Django HttpRequest object

        Returns:
            Dictionary containing IP tracking information
        """
        return {
            'ip_address': getattr(request, 'ip_address', 'Unknown'),
            'user_agent': getattr(request, 'user_agent', ''),
            'device_info': getattr(request, 'device_info', {}),
            'ip_info': getattr(request, 'ip_info', {}),
            'location': getattr(request, 'location', 'Unknown location'),
            'country': getattr(request, 'country', ''),
            'country_code': getattr(request, 'country_code', ''),
            'continent': getattr(request, 'continent', ''),
            'continent_code': getattr(request, 'continent_code', ''),
        }
