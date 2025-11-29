import logging
from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from common.models import BaseModel

logger = logging.getLogger(__name__)


class MyUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class UserModel(AbstractBaseUser, BaseModel, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    profile_picture = models.TextField(
        null=True, blank=True,
        default="https://avatar.iran.liara.run/public/36",
    )
    signature_file = models.ImageField(
        upload_to='signatures/',
        null=True,
        blank=True,
        help_text="User's signature image file"
    )

    # Account status fields
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    # Lock account fields
    failed_login_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    lock_expiry = models.DateTimeField(null=True, blank=True)

    last_password_change_time = models.DateTimeField(null=True, blank=True)

    # Signature authentication
    signature_pin = models.CharField(max_length=128, null=True, blank=True, help_text="Hashed PIN for signature authentication")
    two_factor_enabled = models.BooleanField(default=False, help_text="Whether 2FA is enabled for signatures")
    two_factor_secret = models.CharField(max_length=32, null=True, blank=True, help_text="TOTP secret for 2FA")
    
    # User profile fields for document signing
    designation = models.CharField(max_length=255, null=True, blank=True, help_text="User's job designation/title")
    division = models.CharField(max_length=255, null=True, blank=True, help_text="User's division/department")

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', ]

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def reset_password(self, password="111222"):
        """
        Reset user password
        """
        self.set_password(password)
        self.save()

    def update_last_login(self):
        """
        Updates the last login time for the user.
        """
        logger.info(f"Updating last login time for user: {self.email}")
        try:
            self.last_login = timezone.now()
            self.save(update_fields=['last_login'])
        except Exception as e:
            logger.error(f"Error updating last login time: {e}")

    def update_profile_picture(self, profile_picture):
        """
        Updates the user's profile picture.

        :param profile_picture: Profile picture URL.
        """
        logger.info(f"Updating profile picture for user: {self.email}")
        try:
            self.profile_picture = profile_picture
            self.save(update_fields=['profile_picture'])
            logger.info(f"Profile picture updated successfully.")
        except Exception as e:
            logger.error(f"Error updating profile picture: {e}")

    def increment_failed_login(self):
        """
        Increment failed login attempts and lock account if necessary
        """
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.is_locked = True
            self.lock_expiry = timezone.now() + timedelta(minutes=30)
        self.save()

    def reset_failed_login(self):
        """
        Reset failed login attempts
        """
        self.failed_login_attempts = 0
        self.is_locked = False
        self.lock_expiry = None
        self.save()

    def check_account_status(self):
        """
        Check if account is locked and unlock if lock period has expired
        """
        if self.is_locked and self.lock_expiry and timezone.now() > self.lock_expiry:
            self.is_locked = False
            self.lock_expiry = None
            self.failed_login_attempts = 0
            self.save()
        return not self.is_locked

    @staticmethod
    def check_object_permissions(request, obj):
        if request.user.is_superuser:
            return True
        if request.user.is_admin:
            return True
        if request.user == obj.created_by:
            return True
        if request.user.id == obj.id:
            return True
        return False

    def has_perm(self, perm, obj=None):
        """
        Check if user has a specific permission.
        Only superusers get all permissions automatically.
        For admin users, check if they have the specific permission assigned.
        """
        if self.is_superuser:
            return True
        if self.is_admin:
            # Check if the user has the specific permission assigned
            return super().has_perm(perm, obj)
        return False

    def has_module_perms(self, app_label):
        """
        Check if user has permissions for a specific module.
        Only superusers get all module permissions automatically.
        For admin users, check if they have any permissions for the module.
        """
        if self.is_superuser:
            return True
        if self.is_admin:
            # Check if the user has any permissions for this module
            return super().has_module_perms(app_label)
        return False

    def set_pin(self, pin):
        """
        Set PIN for signature authentication
        """
        from django.contrib.auth.hashers import make_password
        self.signature_pin = make_password(pin)
        self.save(update_fields=['signature_pin'])

    def check_pin(self, pin):
        """
        Check if the provided PIN matches the stored PIN
        """
        from django.contrib.auth.hashers import check_password
        if not self.signature_pin:
            return False
        return check_password(pin, self.signature_pin)

    def setup_two_factor(self):
        """
        Generate and return a new TOTP secret for 2FA
        """
        import pyotp
        secret = pyotp.random_base32()
        self.two_factor_secret = secret
        self.two_factor_enabled = True
        self.save(update_fields=['two_factor_secret', 'two_factor_enabled'])
        return secret

    def verify_totp(self, code):
        """
        Verify a TOTP code
        """
        import pyotp
        if not self.two_factor_secret:
            return False
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(code, valid_window=1)

    def get_totp_uri(self):
        """
        Get the TOTP provisioning URI for QR code generation
        """
        import pyotp
        if not self.two_factor_secret:
            return None
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.provisioning_uri(
            name=self.email,
            issuer_name='Document Generator'
        )


class LoginAttemptModel(BaseModel):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE, related_name='login_attempts',
        null=True, blank=True,
    )
    email = models.EmailField(default="dummy@dummy.com")
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'login_attempts'
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'
        indexes = [
            models.Index(fields=['ip_address'], name='login_attempt_ip_idx'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {'Success' if self.success else 'Failed'}"
