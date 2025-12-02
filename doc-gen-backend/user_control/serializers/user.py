import logging
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from user_control.models import UserModel

logger = logging.getLogger(__name__)


class UserModelSerializerMeta(serializers.ModelSerializer):
    """Base meta class for UserModelSerializer"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        ref_name = 'UserModelSerializer'
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'profile_picture',
            'signature_file',
            'is_verified',
            'is_staff',
            'is_admin',
            'designation',
            'division',
            'two_factor_enabled',
            'created_at',
            'updated_at',
            'last_login',
        ]
        read_only_fields = [
            'id',
            'email',
            'is_verified',
            'is_staff',
            'is_admin',
            'created_at',
            'updated_at',
            'last_login',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserModelSerializer(UserModelSerializerMeta):
    """Full serializer for user data"""
    pass


UserModelSerializer.Lite = type('Lite', (UserModelSerializerMeta,), {
    'Meta': type('Meta', (UserModelSerializerMeta.Meta,), {
        'fields': [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'designation',
            'division',
        ]
    })
})


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = UserModel
        fields = [
            'email',
            'first_name',
            'last_name',
            'password',
            'password_confirm',
        ]

    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Password fields didn't match."
            })
        return attrs

    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = UserModel.objects.create_user(
            password=password,
            **validated_data
        )

        logger.info(f'[UserRegistrationSerializer] User created: {user.email}')
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile (designation and division)"""

    class Meta:
        model = UserModel
        fields = ['designation', 'division']

    def validate_designation(self, value):
        """Validate designation field"""
        if value and len(value.strip()) == 0:
            return None
        return value.strip() if value else None

    def validate_division(self, value):
        """Validate division field"""
        if value and len(value.strip()) == 0:
            return None
        return value.strip() if value else None


class SignatureUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading signature file"""
    signature_file = serializers.ImageField(required=True)

    class Meta:
        model = UserModel
        fields = ['signature_file']

    def validate_signature_file(self, value):
        """Validate signature file"""
        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Signature file size cannot exceed 5MB")

        # Check file type
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("Only image files are allowed")

        return value


class PINSetupSerializer(serializers.Serializer):
    """Serializer for setting up signature PIN"""
    pin = serializers.CharField(
        required=True,
        min_length=4,
        max_length=20,
        write_only=True
    )

    def validate_pin(self, value):
        """Validate PIN"""
        if not value or len(value.strip()) < 4:
            raise serializers.ValidationError("PIN must be at least 4 characters")
        return value.strip()

    def save(self, user):
        """Save hashed PIN to user"""
        pin = self.validated_data['pin']
        user.signature_pin = make_password(pin)
        user.save()
        logger.info(f'[PINSetupSerializer] PIN set for user: {user.email}')
        return user


class TwoFactorSetupSerializer(serializers.Serializer):
    """Serializer for 2FA setup"""
    action = serializers.ChoiceField(
        choices=['enable', 'disable'],
        required=True
    )

    def validate(self, attrs):
        """Validate 2FA setup request"""
        return attrs
