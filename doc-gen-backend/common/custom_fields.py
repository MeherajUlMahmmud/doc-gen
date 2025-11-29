from rest_framework.fields import TimeField


class TimeField12Hour(TimeField):
    """Custom TimeField that formats time in 12-hour format with AM/PM"""

    def to_representation(self, value):
        if value is None:
            return None
        return value.strftime('%I:%M %p')
