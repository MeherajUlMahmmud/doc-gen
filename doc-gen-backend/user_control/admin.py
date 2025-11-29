from django.contrib import admin
from django.db import transaction
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin, ExportMixin

from common.admin import RawIdFieldsAdmin, CommonAdminMixin
from .models import (
    UserModel, LoginAttemptModel,
)


@admin.register(UserModel)
class UserModelAdmin(CommonAdminMixin, ImportExportModelAdmin, RawIdFieldsAdmin):
    list_display = (
        'email', 'get_full_name', 'get_profile_picture',
        'is_verified', 'is_staff', 'is_admin', 'is_superuser', 'last_login',
        'is_locked', 'failed_login_attempts',
    )
    list_filter = (
        'is_verified', 'is_staff', 'is_admin', 'is_superuser',
        'is_locked', 'last_login',
    )
    search_fields = (
        'email', 'first_name', 'last_name',
    )
    readonly_fields = (
        'password', 'last_login', 'get_profile_picture_display',
        'last_password_change_time', 'failed_login_attempts',
    )
    filter_horizontal = ('groups', 'user_permissions')
    fieldsets = (
        (None, {'fields': (
            'id', 'email', 'first_name', 'last_name',
            'profile_picture', 'get_profile_picture_display',
        )}),
        ('Authentication', {'fields': (
            'password',
            'last_password_change_time', 'last_login',
            'failed_login_attempts', 'is_locked', 'lock_expiry',
        )}),
        ('Permissions', {'fields': (
            'is_verified', 'is_staff', 'is_admin', 'is_superuser',
            'groups', 'user_permissions',
        )}),
    )
    fieldsets += CommonAdminMixin().get_common_fieldsets()

    actions = ['reset_password', 'verify_users', 'unlock_users', 'lock_users']

    def get_full_name(self, obj):
        return obj.get_full_name()

    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'first_name'

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover;" />',
                obj.profile_picture
            )
        return "No Image"

    get_profile_picture.short_description = 'Profile Picture'

    def get_profile_picture_display(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover;" />',
                obj.profile_picture
            )
        return "No Image"

    get_profile_picture_display.short_description = 'Profile Picture'

    def reset_password(self, request, queryset):
        count = 0
        with transaction.atomic():
            for user in queryset:
                user.reset_password()
                count += 1
        self.message_user(
            request, f'Password reset successfully for {count} users')

    reset_password.short_description = 'Reset Password to "111222"'

    def verify_users(self, request, queryset):
        count = queryset.update(is_verified=True)
        self.message_user(request, f'Verified {count} users successfully')

    verify_users.short_description = 'Mark selected users as verified'

    def unlock_users(self, request, queryset):
        count = queryset.update(
            is_locked=False, failed_login_attempts=0, lock_expiry=None)
        self.message_user(request, f'Unlocked {count} users successfully')

    unlock_users.short_description = 'Mark selected users as unlocked'

    def lock_users(self, request, queryset):
        count = queryset.update(is_locked=True)
        self.message_user(request, f'Locked {count} users successfully')

    lock_users.short_description = 'Lock selected users'


@admin.register(LoginAttemptModel)
class LoginAttemptAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        'email', 'ip_address', 'success', 'reason', 'get_user_full_name',
        'created_at',
    )
    list_filter = ('success', 'created_at', 'ip_address')
    search_fields = ('email', 'ip_address', 'user_agent', 'reason')
    ordering = ('-created_at',)
    readonly_fields = (
        'user', 'email', 'ip_address', 'user_agent', 'success', 'reason',
        'get_user_full_name',
    )
    raw_id_fields = ('user',)

    fieldsets = (
        (None, {'fields': (
            'id', 'email', 'user', 'get_user_full_name', 'ip_address', 'user_agent',
            'success', 'reason',
        )}),
    )
    fieldsets += CommonAdminMixin().get_common_fieldsets()

    def get_user_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else "No User"

    get_user_full_name.short_description = 'User Full Name'
    get_user_full_name.admin_order_field = 'user__first_name'

    def has_add_permission(self, request):
        return False  # Prevent manual addition of login attempts

    def has_change_permission(self, request, obj=None):
        return False  # Prevent modification of login attempts

    def has_delete_permission(self, request, obj=None):
        return True  # Allow deletion for cleanup purposes
