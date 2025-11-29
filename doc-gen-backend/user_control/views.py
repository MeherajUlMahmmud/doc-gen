import logging
import base64
import qrcode
from io import BytesIO
from datetime import datetime, timezone

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from django.utils import timezone as django_timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from common.api_response import ApiResponse
from common.custom_view import CustomCreateAPIView, CustomRetrieveAPIView, CustomUpdateAPIView
from user_control.models import UserModel, LoginAttemptModel
from user_control.serializers.user import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileUpdateSerializer,
    SignatureUploadSerializer,
    PINSetupSerializer,
    TwoFactorSetupSerializer,
)

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class RegisterAPIView(CustomCreateAPIView):
    """User registration API view"""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    queryset = UserModel.objects.all()

    def create(self, request, *args, **kwargs):
        logger.info('[RegisterAPIView] User registration request received')

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            logger.info('[RegisterAPIView] Registration data validation successful')
        except Exception as e:
            logger.error(f'[RegisterAPIView] Validation error: {str(e)}')
            return ApiResponse.bad_request(
                message='Validation failed',
                errors=serializer.errors if hasattr(serializer, 'errors') else str(e)
            )

        try:
            user = serializer.save()
            logger.info(f'[RegisterAPIView] User registration successful for email: {user.email}')

            return ApiResponse.created(
                message='User registration successful',
                data=UserSerializer(user).data
            )
        except Exception as e:
            logger.error(f'[RegisterAPIView] Unexpected error during user registration: {str(e)}')
            return ApiResponse.server_error(message='Registration failed due to an unexpected error')


class LoginAPIView(GenericAPIView):
    """User login API view with account locking"""
    permission_classes = [AllowAny]
    serializer_class = None  # No specific serializer needed

    def post(self, request):
        logger.info('[LoginAPIView] Login request received')

        email = request.data.get('email')
        password = request.data.get('password')
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        logger.info(f'[LoginAPIView] Login attempt from IP: {ip_address}')

        # Validate input
        if not email or not password:
            return ApiResponse.bad_request(message='Email and password are required')

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            logger.warning(f'[LoginAPIView] Login attempt for non-existent email: {email}')
            return ApiResponse.unauthorized(message='Invalid email or password')

        # Check if account is locked
        if not user.check_account_status():
            logger.warning(f'[LoginAPIView] Login attempt for locked account: {email}')
            LoginAttemptModel.objects.create(
                user=user,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                reason='Account locked'
            )
            return ApiResponse.forbidden(message='Your account is locked. Please try again later.')

        # # Check if account is verified (optional - can be removed if not needed)
        # if not user.is_verified and not user.is_staff:
        #     logger.warning(f'[LoginAPIView] Login attempt for unverified account: {email}')
        #     LoginAttemptModel.objects.create(
        #         user=user,
        #         email=email,
        #         ip_address=ip_address,
        #         user_agent=user_agent,
        #         success=False,
        #         reason='Account not verified'
        #     )
        #     return ApiResponse.unauthorized(
        #         message='Your account is not verified yet. Please contact an administrator.'
        #     )

        # Authenticate user
        authenticated_user = authenticate(request, username=email, password=password)

        if authenticated_user is not None:
            # Successful login
            user.reset_failed_login()
            user.update_last_login()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Log successful attempt
            LoginAttemptModel.objects.create(
                user=user,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )

            logger.info(f'[LoginAPIView] User {user.email} logged in successfully from IP: {ip_address}')

            return ApiResponse.success(
                message='Login successful',
                data={
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': access_token,
                        'refresh': refresh_token,
                    }
                }
            )
        else:
            # Failed authentication
            user.increment_failed_login()

            LoginAttemptModel.objects.create(
                user=user,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                reason='Invalid password'
            )

            logger.warning(f'[LoginAPIView] Invalid password for email: {email}')
            return ApiResponse.unauthorized(message='Invalid email or password')


class RefreshTokenAPIView(GenericAPIView):
    """Refresh access token using refresh token"""
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info('[RefreshTokenAPIView] Token refresh request received')

        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return ApiResponse.bad_request(message='Refresh token is required')

        try:
            # Get refresh token and generate new access token
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)

            logger.info('[RefreshTokenAPIView] Token refreshed successfully')

            return ApiResponse.success(
                message='Token refreshed successfully',
                data={
                    'access': new_access_token
                }
            )

        except TokenError as e:
            logger.error(f'[RefreshTokenAPIView] Token error: {str(e)}')
            return ApiResponse.unauthorized(message='Invalid or expired refresh token')
        except Exception as e:
            logger.error(f'[RefreshTokenAPIView] Error refreshing token: {str(e)}')
            return ApiResponse.server_error(message='Token refresh failed')


class LogoutAPIView(GenericAPIView):
    """User logout API view - blacklist refresh token"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f'[LogoutAPIView] Logout request received from user: {request.user.email}')

        try:
            refresh_token = request.data.get('refresh_token')

            if not refresh_token:
                return ApiResponse.bad_request(message='Refresh token is required')

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(f'[LogoutAPIView] User {request.user.email} logged out successfully')
            return ApiResponse.success(message='Logout successful', status_code=status.HTTP_204_NO_CONTENT)

        except TokenError as e:
            logger.error(f'[LogoutAPIView] Token error during logout for user {request.user.email}: {str(e)}')
            return ApiResponse.bad_request(message='Invalid or expired token')
        except Exception as e:
            logger.error(f'[LogoutAPIView] Error during logout for user {request.user.email}: {str(e)}')
            return ApiResponse.server_error(message='Logout failed')


class ProfileRetrieveAPIView(CustomRetrieveAPIView):
    """Retrieve user profile"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = UserModel.objects.filter(is_active=True, is_deleted=False)

    def get_object(self):
        """Return the current user"""
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        logger.info(f'[ProfileRetrieveAPIView] Profile retrieval request from user: {request.user.email}')

        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return ApiResponse.success(
            message='Profile retrieved successfully',
            data=serializer.data
        )


class ProfileUpdateAPIView(CustomUpdateAPIView):
    """Update user profile (designation and division)"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileUpdateSerializer
    queryset = UserModel.objects.filter(is_active=True, is_deleted=False)

    def get_object(self):
        """Return the current user"""
        return self.request.user

    def update(self, request, *args, **kwargs):
        logger.info(f'[ProfileUpdateAPIView] Profile update request from user: {request.user.email}')

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f'[ProfileUpdateAPIView] Profile updated successfully for user: {request.user.email}')

            return ApiResponse.success(
                message='Profile updated successfully',
                data=UserSerializer(instance).data
            )
        except Exception as e:
            logger.error(f'[ProfileUpdateAPIView] Error updating profile for user {request.user.email}: {str(e)}')
            return ApiResponse.bad_request(
                message='Failed to update profile',
                errors=serializer.errors if hasattr(serializer, 'errors') else str(e)
            )


class SignatureUploadAPIView(CustomUpdateAPIView):
    """Upload user signature"""
    permission_classes = [IsAuthenticated]
    serializer_class = SignatureUploadSerializer
    queryset = UserModel.objects.filter(is_active=True, is_deleted=False)

    def get_object(self):
        """Return the current user"""
        return self.request.user

    def update(self, request, *args, **kwargs):
        logger.info(f'[SignatureUploadAPIView] Signature upload request from user: {request.user.email}')

        if 'signature_file' not in request.FILES:
            return ApiResponse.bad_request(message='No signature file provided')

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f'[SignatureUploadAPIView] Signature uploaded successfully for user: {request.user.email}')

            return ApiResponse.success(
                message='Signature uploaded successfully',
                data={
                    'signature_file': instance.signature_file.url if instance.signature_file else None
                }
            )
        except Exception as e:
            logger.error(f'[SignatureUploadAPIView] Error uploading signature for user {request.user.email}: {str(e)}')
            return ApiResponse.bad_request(
                message='Failed to upload signature',
                errors=serializer.errors if hasattr(serializer, 'errors') else str(e)
            )


class PINSetupAPIView(GenericAPIView):
    """Setup or change signature PIN"""
    permission_classes = [IsAuthenticated]
    serializer_class = PINSetupSerializer

    def post(self, request):
        logger.info(f'[PINSetupAPIView] PIN setup request from user: {request.user.email}')

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            logger.info(f'[PINSetupAPIView] PIN set successfully for user: {request.user.email}')

            return ApiResponse.success(message='PIN set successfully')
        except Exception as e:
            logger.error(f'[PINSetupAPIView] Error setting PIN for user {request.user.email}: {str(e)}')
            return ApiResponse.bad_request(
                message='Failed to set PIN',
                errors=serializer.errors if hasattr(serializer, 'errors') else str(e)
            )


class TwoFactorSetupAPIView(GenericAPIView):
    """Setup 2FA for signatures"""
    permission_classes = [IsAuthenticated]
    serializer_class = TwoFactorSetupSerializer

    def get(self, request):
        """Get QR code for 2FA setup"""
        logger.info(f'[TwoFactorSetupAPIView] 2FA QR code request from user: {request.user.email}')

        try:
            import pyotp
        except ImportError:
            logger.error('[TwoFactorSetupAPIView] pyotp library not installed')
            return ApiResponse.server_error(message='2FA service unavailable')

        user = request.user

        # Generate secret if doesn't exist
        if not user.two_factor_secret:
            secret = pyotp.random_base32()
            user.two_factor_secret = secret
            user.save()
        else:
            secret = user.two_factor_secret

        # Generate QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name='Document Generator'
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        qr_code_data = base64.b64encode(buffer.read()).decode()

        logger.info(f'[TwoFactorSetupAPIView] QR code generated for user: {user.email}')

        return ApiResponse.success(
            message='QR code generated successfully',
            data={
                'qr_code': f'data:image/png;base64,{qr_code_data}',
                'secret': secret,
                'two_factor_enabled': user.two_factor_enabled
            }
        )

    def post(self, request):
        """Enable or disable 2FA"""
        logger.info(f'[TwoFactorSetupAPIView] 2FA toggle request from user: {request.user.email}')

        try:
            import pyotp
        except ImportError:
            logger.error('[TwoFactorSetupAPIView] pyotp library not installed')
            return ApiResponse.server_error(message='2FA service unavailable')

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            action = serializer.validated_data['action']
            user = request.user

            if action == 'enable':
                # Generate new secret if doesn't exist
                if not user.two_factor_secret:
                    secret = pyotp.random_base32()
                    user.two_factor_secret = secret

                user.two_factor_enabled = True
                user.save()

                # Generate QR code
                totp_uri = pyotp.totp.TOTP(user.two_factor_secret).provisioning_uri(
                    name=user.email,
                    issuer_name='Document Generator'
                )

                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(totp_uri)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)

                qr_code_data = base64.b64encode(buffer.read()).decode()

                logger.info(f'[TwoFactorSetupAPIView] 2FA enabled for user: {user.email}')

                return ApiResponse.success(
                    message='2FA enabled successfully',
                    data={
                        'qr_code': f'data:image/png;base64,{qr_code_data}',
                        'secret': user.two_factor_secret
                    }
                )
            else:  # disable
                user.two_factor_enabled = False
                user.save()

                logger.info(f'[TwoFactorSetupAPIView] 2FA disabled for user: {user.email}')

                return ApiResponse.success(message='2FA disabled successfully')

        except Exception as e:
            logger.error(f'[TwoFactorSetupAPIView] Error toggling 2FA for user {request.user.email}: {str(e)}')
            return ApiResponse.bad_request(
                message='Failed to toggle 2FA',
                errors=serializer.errors if hasattr(serializer, 'errors') else str(e)
            )
