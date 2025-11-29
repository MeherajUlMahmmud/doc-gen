import logging
from typing import Dict, Optional

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from common.api_response import ApiResponse
from common.exceptions import format_serializer_errors

logger = logging.getLogger(__name__)


def handle_serializer_validation_error(
        serializer: serializers.Serializer,
        user_email: str,
        view_name: str,
        friendly_messages: Optional[Dict[str, str]] = None
) -> ApiResponse:
    """
    Centralized handler for serializer validation errors.
    
    Args:
        serializer: The serializer with validation errors
        user_email: User email for logging
        view_name: Name of the view for logging
        friendly_messages: Optional mapping of field names to friendly error messages
        
    Returns:
        ApiResponse: Formatted error response with the first error message
    """
    logger.warning(f'[{view_name}] Validation failed. User: {user_email}, Errors: {serializer.errors}')

    # Extract the first error message
    error_message = format_serializer_errors(serializer.errors)

    # If friendly messages are provided, try to use them
    if friendly_messages and serializer.errors:
        first_field = next(iter(serializer.errors))
        if first_field in friendly_messages:
            error_message = friendly_messages[first_field]

    logger.info(f'[{view_name}] Returning error message: {error_message}')

    return ApiResponse.bad_request(message=error_message)


def handle_validation_error(
        exc: ValidationError,
        user_email: str,
        view_name: str
) -> ApiResponse:
    """
    Centralized handler for ValidationError exceptions.
    
    Args:
        exc: The ValidationError exception
        user_email: User email for logging
        view_name: Name of the view for logging
        
    Returns:
        ApiResponse: Formatted error response with the first error message
    """
    logger.warning(f'[{view_name}] Validation error. User: {user_email}, Error: {str(exc)}')

    # Extract the first error message
    if hasattr(exc, 'detail') and exc.detail:
        error_message = format_serializer_errors(exc.detail)
    else:
        error_message = str(exc)

    logger.info(f'[{view_name}] Returning error message: {error_message}')

    return ApiResponse.bad_request(message=error_message)


def create_friendly_error_messages() -> Dict[str, str]:
    """
    Common friendly error messages that can be used across views.
    
    Returns:
        Dict[str, str]: Mapping of field names to friendly error messages
    """
    return {
        'email': "Please provide a valid email address.",
        'phone': "Enter a valid phone number.",
        'password': "Password does not meet security requirements.",
        'first_name': "First name can only contain letters and spaces.",
        'last_name': "Last name can only contain letters and spaces.",
        'job': "The selected job is invalid or unavailable.",
        'services': "One or more selected services are invalid or unavailable.",
        'date': "Make sure the date is correct and in the future.",
        'time': "The selected time is not valid.",
        'start_time': "The start time is invalid.",
        'end_time': "The finish time is invalid.",
        'employee_rates': "The employee rate data is invalid.",
        'note': "The note content is invalid.",
        'job_slot': "The selected job slot is invalid or unavailable.",
        'check_in_images': "Image upload failed. Please check file format and size.",
        'check_out_images': "Image upload failed. Please check file format and size.",
    }
