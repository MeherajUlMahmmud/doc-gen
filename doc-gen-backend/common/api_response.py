import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from common.constants.error_messages import ErrorMessage

logger = logging.getLogger(__name__)


class ApiResponse:
    """
    Standardizes API responses across the application.
    Provides methods for success and error responses with consistent structure.
    """

    @staticmethod
    def format_response(data=None, message=None, status_code=status.HTTP_200_OK, errors=None, meta=None):
        """
        Creates a standardized response object

        Args:
            data: The response data (can be any serializable object)
            message: A message describing the response
            status_code: HTTP status code
            errors: List of error details or error object
            meta: Additional metadata (pagination info, etc.)

        Returns:
            Response: DRF Response object with standardized format
        """
        response_body = {
            "status": "success" if status.is_success(status_code) else "error",
            "status_code": status_code,
        }

        if message:
            response_body["message"] = message

        if data is not None:
            response_body["data"] = data

        if errors is not None:
            response_body["errors"] = errors

        if meta is not None:
            response_body["meta"] = meta

        # Add request ID if available in debug mode
        if settings.DEBUG and hasattr(settings, 'REQUEST_ID_HEADER'):
            response_body["request_id"] = settings.REQUEST_ID_HEADER

        return Response(response_body, status=status_code)

    @staticmethod
    def success(data=None, message="Operation successful", status_code=status.HTTP_200_OK, meta=None):
        """
        Creates a success response
        """
        return ApiResponse.format_response(
            data=data,
            message=message,
            status_code=status_code,
            meta=meta
        )

    @staticmethod
    def created(data=None, message="Resource created successfully", meta=None):
        """
        Creates a resource creation success response (HTTP 201)
        """
        return ApiResponse.format_response(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED,
            meta=meta
        )

    @staticmethod
    def error(message="An error occurred", status_code=status.HTTP_400_BAD_REQUEST, errors=None, meta=None):
        """
        Creates an error response
        """
        # Log error for server-side errors
        if status_code >= 500:
            logger.error(f"Server error: {message}", exc_info=True)

        return ApiResponse.format_response(
            message=message,
            status_code=status_code,
            errors=errors,
            meta=meta
        )

    @staticmethod
    def bad_request(message=ErrorMessage.INVALID_REQUEST, errors=None):
        """
        Creates a bad request error response (HTTP 400)
        """
        return ApiResponse.error(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=errors
        )

    @staticmethod
    def unauthorized(message=ErrorMessage.AUTHENTICATION_FAILED, errors=None):
        """
        Creates an unauthorized error response (HTTP 401)
        """
        return ApiResponse.error(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=errors
        )

    @staticmethod
    def forbidden(message=ErrorMessage.PERMISSION_DENIED, errors=None):
        """
        Creates a forbidden error response (HTTP 403)
        """
        return ApiResponse.error(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            errors=errors
        )

    @staticmethod
    def not_found(message="Resource not found", errors=None):
        """
        Creates a not found error response (HTTP 404)
        """
        return ApiResponse.error(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            errors=errors
        )

    @staticmethod
    def validation_error(errors, message="Validation failed"):
        """
        Creates a validation error response (HTTP 422)
        """
        return ApiResponse.error(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=errors
        )

    @staticmethod
    def server_error(message=ErrorMessage.INTERNAL_SERVER_ERROR, errors=None):
        """
        Creates a server error response (HTTP 500)
        """
        return ApiResponse.error(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            # errors=errors
        )
