import logging
import re
from typing import Any, Dict, Union

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import exception_handler as drf_exception_handler

from common.api_response import ApiResponse

logger = logging.getLogger(__name__)


def extract_first_error_message(error_detail: Any) -> str:
    """
    Extract the first error message from various error detail formats.
    
    Args:
        error_detail: Error detail from ValidationError or serializer.errors
        
    Returns:
        str: The first error message as a string
    """
    if not error_detail:
        return "Validation failed"

    # Handle string errors
    if isinstance(error_detail, str):
        return error_detail

    # Handle list errors
    if isinstance(error_detail, list):
        if error_detail:
            return str(error_detail[0])
        return "Validation failed"

    # Handle dictionary errors (field-based errors)
    if isinstance(error_detail, dict):
        if not error_detail:
            return "Validation failed"

        # Get the first field with errors
        first_field = next(iter(error_detail))
        first_field_errors = error_detail[first_field]

        # Handle nested field errors
        if isinstance(first_field_errors, dict):
            return extract_first_error_message(first_field_errors)

        # Handle list of field errors
        if isinstance(first_field_errors, list):
            if first_field_errors:
                return str(first_field_errors[0])
            return f"Field '{first_field}' has validation errors"

        # Handle single field error
        return str(first_field_errors)

    # Handle other types
    return str(error_detail)


def handle_validation_error(exc: Union[DRFValidationError, DjangoValidationError, serializers.ValidationError],
                            context: Dict[str, Any]) -> ApiResponse:
    """
    Handle all types of validation errors and return a consistent response.
    
    Args:
        exc: The validation error exception
        context: DRF context
        
    Returns:
        ApiResponse: Formatted error response
    """
    logger.warning(f"Validation failed: {type(exc).__name__}", exc_info=True)

    # Extract error message based on exception type
    if isinstance(exc, DRFValidationError):
        # DRF ValidationError from serializers or views
        error_message = extract_first_error_message(exc.detail)
    elif isinstance(exc, DjangoValidationError):
        # Django ValidationError from validators
        error_message = extract_first_error_message(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)
    elif isinstance(exc, serializers.ValidationError):
        # Serializer ValidationError
        error_message = extract_first_error_message(exc.detail)
    else:
        # Fallback
        error_message = str(exc)

    logger.info(f"Returning first validation error: {error_message}")
    return ApiResponse.bad_request(message=error_message)


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> ApiResponse:
    """
    Centralized exception handler for all API errors.
    
    Args:
        exc: The exception that occurred
        context: DRF context
        
    Returns:
        ApiResponse: Formatted error response
    """
    # Handle all types of validation errors first - BEFORE calling DRF handler
    if isinstance(exc, (DRFValidationError, DjangoValidationError, serializers.ValidationError)):
        return handle_validation_error(exc, context)

    # Let DRF handle standard exceptions first
    response = drf_exception_handler(exc, context)

    if response is not None:
        # DRF handled the exception, but we want to format it consistently
        if hasattr(exc, 'detail'):
            error_message = extract_first_error_message(exc.detail)
        else:
            error_message = str(exc)

        return ApiResponse.error(
            message=error_message,
            status_code=response.status_code
        )

    # Handle Django database integrity errors
    if isinstance(exc, IntegrityError):
        logger.error("Database integrity error", exc_info=True)
        msg = str(exc)

        # Extract field name from unique constraint errors
        match = re.search(r'Key \((.*?)\)=\((.*?)\)', msg)
        if match:
            field, value = match.groups()
            return ApiResponse.bad_request(
                message=f"A record with this {field} already exists."
            )

        return ApiResponse.bad_request(
            message="A data integrity error occurred."
        )

    # Catch-all for unhandled exceptions
    logger.critical(f"Unhandled server error: {type(exc).__name__}", exc_info=True)
    return ApiResponse.server_error()


def format_serializer_errors(serializer_errors: Dict[str, Any]) -> str:
    """
    Utility function to extract the first error message from serializer.errors.
    This can be used in views when you want to handle serializer validation manually.
    
    Args:
        serializer_errors: The errors from serializer.errors
        
    Returns:
        str: The first error message as a string
    """
    return extract_first_error_message(serializer_errors)
