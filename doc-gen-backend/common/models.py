import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, editable=False,
        unique=True, primary_key=True,
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'user_control.UserModel', related_name='%(class)s_created_by',
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    updated_by = models.ForeignKey(
        'user_control.UserModel', related_name='%(class)s_updated_by',
        on_delete=models.SET_NULL, null=True, blank=True,
    )

    class Meta:
        abstract = True


class RequestLog(BaseModel):
    user = models.ForeignKey(
        'user_control.UserModel', on_delete=models.CASCADE,
        null=True, blank=True,
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    endpoint = models.CharField(max_length=255, null=True, blank=True)
    method = models.CharField(max_length=10, default="")
    request_body = models.TextField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    trace_id = models.CharField(max_length=50, null=True, blank=True)
    response_time = models.FloatField(
        help_text="Time taken to process request (in seconds)", null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    objects = models.Manager()

    class Meta:
        db_table = 'request_logs'
        verbose_name = 'Request Log'
        verbose_name_plural = 'Request Logs'
        ordering = ['-created_at']

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'Anonymous'
        return f"{user_name} - {self.method} {self.endpoint} - {self.status_code} - {self.created_at}"


class BlockedIPModel(BaseModel):
    ip_address = models.CharField(max_length=45, unique=True)
    reason = models.CharField(max_length=255, default="Sensitive file access attempt")
    attempts = models.IntegerField(default=1)
    first_attempt = models.DateTimeField(auto_now_add=True)
    last_attempt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blocked_ips'
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"

    def __str__(self):
        return f"{self.ip_address} - {'Blocked' if self.is_active else 'Unblocked'}"


class IPTrackingModel(BaseModel):
    """
    Model to store IP tracking and geolocation data for API requests.
    This data is automatically collected by the IPTrackingMiddleware.
    """
    user = models.ForeignKey(
        'user_control.UserModel', on_delete=models.CASCADE,
        null=True, blank=True,
    )
    ip_address = models.GenericIPAddressField()
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    user_agent = models.TextField(null=True, blank=True)

    # Device information
    device_type = models.CharField(max_length=50, null=True, blank=True)
    browser = models.CharField(max_length=50, null=True, blank=True)
    operating_system = models.CharField(max_length=50, null=True, blank=True)

    # Location information
    country = models.CharField(max_length=100, null=True, blank=True)
    country_code = models.CharField(max_length=10, null=True, blank=True)
    continent = models.CharField(max_length=50, null=True, blank=True)
    continent_code = models.CharField(max_length=10, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    region_name = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)

    # Geographic coordinates
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8,
        null=True, blank=True,
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8,
        null=True, blank=True,
    )

    # Additional information
    timezone = models.CharField(max_length=50, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    isp = models.CharField(max_length=255, null=True, blank=True)
    organization = models.CharField(max_length=255, null=True, blank=True)
    as_number = models.CharField(max_length=50, null=True, blank=True)
    is_mobile = models.BooleanField(null=True, blank=True)

    # Request tracking
    trace_id = models.CharField(max_length=50, null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    response_time = models.FloatField(help_text="Time taken to process request (in seconds)", null=True, blank=True)

    class Meta:
        db_table = 'ip_tracking'
        verbose_name = 'IP Tracking'
        verbose_name_plural = 'IP Tracking'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['country']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'Anonymous'
        return f"{user_name} - {self.ip_address} - {self.country} - {self.created_at}"
