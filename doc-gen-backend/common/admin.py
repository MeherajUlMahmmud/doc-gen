from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from common.models import (
    BaseModel, RequestLog, BlockedIPModel, IPTrackingModel,
)


class CommonAdminMixin:

    def save_model(self, request, obj, form, change):
        if change:  # Only set updated_by if this is an update, not a creation
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
        obj.save()

    @staticmethod
    def get_status_fields():
        return 'is_active', 'is_deleted'

    @staticmethod
    def get_history_fields():
        return 'created_at', 'updated_at', 'created_by', 'updated_by'

    def get_common_fieldsets(self):
        return (
            ('Status', {'fields': self.get_status_fields()}),
            ('Timestamps', {'fields': self.get_history_fields()}),
        )


class RawIdFieldsAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super(RawIdFieldsAdmin, self).__init__(*args, **kwargs)
        # make all ForeignKey fields use raw_id_fields
        # self.raw_id_fields = [
        #     field.name for field in self.model._meta.get_fields() if field.is_relation and field.many_to_one
        # ]

        if issubclass(self.model, BaseModel):
            primary_key = self.model._meta.pk.name
            CREATED_AT = ['created_at']
            UPDATED_AT = ['updated_at']
            # Keep original field name for list_filter
            IS_ACTIVE_FIELD = ['is_active']
            # Use formatted display for list_display
            IS_ACTIVE_DISPLAY = ['is_active_status']
            IS_DELETED = ['is_deleted']
            timestamp_fields = CREATED_AT + UPDATED_AT
            status_fields = IS_ACTIVE_FIELD + IS_DELETED

            self.list_display = [primary_key] + list(self.list_display) + CREATED_AT + IS_ACTIVE_DISPLAY
            self.readonly_fields = [primary_key] + list(self.readonly_fields) + timestamp_fields
            self.list_filter = list(self.list_filter) + CREATED_AT + status_fields
            self.list_per_page = 100

    def is_active_status(self, obj):
        """Format the is_active field as a colored status indicator"""
        if obj.is_active:
            return format_html(
                '<span style="background-color:#dff0d8;padding:3px 8px;border-radius:3px;">Active</span>')
        return format_html('<span style="background-color:#f2dede;padding:3px 8px;border-radius:3px;">Inactive</span>')

    is_active_status.short_description = 'Active Status'


@admin.register(RequestLog)
class RequestLogModelAdmin(CommonAdminMixin, ImportExportModelAdmin, RawIdFieldsAdmin):
    list_display = (
        'user', 'ip_address', 'method', 'endpoint', 'status_code',
        'response_time', 'trace_id',
    )
    list_filter = ('status_code', 'method',)
    search_fields = ('user__email', 'ip_address', 'endpoint', 'trace_id')
    readonly_fields = (
        'user', 'ip_address', 'method', 'endpoint', 'request_body',
        'status_code', 'response', 'user_agent', 'trace_id',
        'response_time', 'error_message',
    )
    fieldsets = (
        ('Request Info', {'fields': ('user', 'ip_address',
                                     'method', 'endpoint', 'request_body')}),
        ('Response Info', {'fields': ('status_code',
                                      'response', 'response_time', 'error_message')}),
        ('Metadata', {'fields': ('user_agent', 'trace_id',)}),
    )
    ordering = ('-created_at',)

    fieldsets += CommonAdminMixin().get_common_fieldsets()


@admin.register(BlockedIPModel)
class BlockedIPModelAdmin(CommonAdminMixin, ImportExportModelAdmin, RawIdFieldsAdmin):
    list_display = (
        'ip_address', 'reason', 'attempts', 'is_active', 'first_attempt', 'last_attempt',
    )
    search_fields = ('ip_address', 'reason')
    readonly_fields = ('first_attempt', 'last_attempt')
    fieldsets = (
        (None, {'fields': (
            'ip_address', 'reason', 'attempts',
        )}),
    )

    fieldsets += CommonAdminMixin().get_common_fieldsets()

    actions = ['block_ips', 'unblock_ips']

    def block_ips(self, request, queryset):
        from django.utils import timezone
        for obj in queryset:
            obj.is_active = True
            obj.created_at = timezone.now()
            obj.save()

    def unblock_ips(self, request, queryset):
        for obj in queryset:
            obj.is_active = False
            obj.save()

    block_ips.short_description = 'Block selected IPs'
    unblock_ips.short_description = 'Unblock selected IPs'


@admin.register(IPTrackingModel)
class IPTrackingModelAdmin(CommonAdminMixin, ImportExportModelAdmin, RawIdFieldsAdmin):
    list_display = (
        'user', 'ip_address', 'method', 'endpoint', 'country', 'city',
        'device_type', 'browser', 'operating_system', 'is_mobile',
    )
    list_filter = (
        'method', 'country', 'continent', 'device_type', 'browser',
        'operating_system', 'is_mobile', 'status_code',
    )
    search_fields = (
        'user__email', 'ip_address', 'endpoint', 'country', 'city',
        'isp', 'organization', 'trace_id',
    )
    readonly_fields = (
        'user', 'ip_address', 'endpoint', 'method', 'user_agent',
        'device_type', 'browser', 'operating_system',
        'country', 'country_code', 'continent', 'continent_code',
        'region', 'region_name', 'city', 'district', 'zip_code',
        'latitude', 'longitude', 'timezone', 'currency',
        'isp', 'organization', 'as_number', 'is_mobile',
        'trace_id', 'status_code', 'response_time',
    )
    fieldsets = (
        ('Request Info', {'fields': ('user', 'ip_address',
                                     'method', 'endpoint', 'user_agent', 'trace_id')}),
        ('Device Info', {'fields': ('device_type',
                                    'browser', 'operating_system', 'is_mobile')}),
        ('Location Info', {'fields': ('country', 'country_code', 'continent',
                                      'continent_code', 'region', 'region_name', 'city', 'district', 'zip_code')}),
        ('Geographic Data', {
            'fields': ('latitude', 'longitude', 'timezone', 'currency')}),
        ('Network Info', {'fields': ('isp', 'organization', 'as_number')}),
        ('Response Info', {'fields': ('status_code', 'response_time')}),
    )
    ordering = ('-created_at',)
    list_per_page = 50

    fieldsets += CommonAdminMixin().get_common_fieldsets()

    def has_add_permission(self, request):
        """Disable manual creation of IP tracking records"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing of IP tracking records"""
        return False
