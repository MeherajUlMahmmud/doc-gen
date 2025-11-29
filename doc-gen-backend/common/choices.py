from django.db import models


class GenderChoices(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other/Non-binary"


class OrderStatusChoices(models.TextChoices):
    PENDING = "pending", "Awaiting Processing"
    IN_PROGRESS = "in_progress", "Being Processed"
    COMPLETED = "completed", "Successfully Completed"
    CANCELED = "canceled", "Order Canceled"


class PaymentMethodChoices(models.TextChoices):
    CASH = "cash", "Cash Payment"
    CREDIT_CARD = "credit_card", "Credit/Debit Card"
    CHECK = "check", "Check Payment"
    OTHER = "other", "Other Payment Method"


class PaymentStatusChoices(models.TextChoices):
    PENDING = "pending", "Payment Pending"
    PAID = "paid", "Payment Confirmed"
    REFUNDED = "refunded", "Refund Processed"
    CANCELED = "canceled", "Payment Canceled"


class UserTypeChoices(models.TextChoices):
    EMPLOYEE = "employee", "Employee"
    CUSTOMER = "customer", "Customer"
    ADMIN = "admin", "Admin"


class JobTypeChoices(models.TextChoices):
    DOMESTIC = "domestic", "Domestic"
    COMMERCIAL = "commercial", "Commercial"


class CurrencyChoices(models.TextChoices):
    USD = "USD", "US Dollar ($)"
    EUR = "EUR", "Euro (€)"
    GBP = "GBP", "British Pound (£)"
    JPY = "JPY", "Japanese Yen (¥)"
    CAD = "CAD", "Canadian Dollar (CAD$)"
    AUD = "AUD", "Australian Dollar (AUD$)"
    CHF = "CHF", "Swiss Franc (CHF)"
    CNY = "CNY", "Chinese Yuan (¥)"
    INR = "INR", "Indian Rupee (₹)"
    BDT = "BDT", "Bangladeshi Taka (৳)"
    SEK = "SEK", "Swedish Krona (kr)"
    NZD = "NZD", "New Zealand Dollar (NZ$)"
    SGD = "SGD", "Singapore Dollar (S$)"


class ServiceCategoryChoices(models.TextChoices):
    DOMESTIC = "domestic", "Domestic"
    COMMERCIAL = "commercial", "Commercial"


class JobStatusChoices(models.TextChoices):
    PENDING = "pending", "Awaiting Start"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Successfully Completed"
    CANCELLED = "cancelled", "Job Cancelled"


class JobProposalStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending Response"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    EXPIRED = "expired", "Expired"


class QuoteRequestStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    QUOTE_CREATED = "quote_created", "Quote Created"
    QUOTE_SENT = "quote_sent", "Quote Sent"


class QuoteStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    QUOTE_SENT = "quote_sent", "Quote Sent"
    ACCEPTED = "accepted", "Accepted"
    ORDER_CREATED = "order_created", "Order Created"
    JOB_CREATED = "job_created", "Job Created"


YesNoChoices = [
    (None, 'All'),
    (True, 'Yes'),
    (False, 'No'),
]

RATING_CHOICES = [
    (1, '1 - Very Poor'),
    (2, '2 - Poor'),
    (3, '3 - Average'),
    (4, '4 - Good'),
    (5, '5 - Excellent'),
]


class QuoteFormFieldTypeChoices(models.TextChoices):
    TEXT = "text", "Text"
    NUMBER = "number", "Number"
    SELECT = "select", "Select/Dropdown"
    RADIO = "radio", "Radio"
    CHECKBOX = "checkbox", "Checkbox"
    DATE = "date", "Date"


class JobSlotStatusChoices(models.TextChoices):
    OPEN = "open", "Open for Invitations"
    PARTIALLY_FILLED = "partially_filled", "Partially Filled"
    FILLED = "filled", "Fully Filled"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class InvitationStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending Response"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    EXPIRED = "expired", "Expired"
    CANCELLED = "cancelled", "Cancelled by Admin"


class RecurrenceTypeChoices(models.TextChoices):
    ONE_OFF = "one_off", "One-time Slot"
    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    BIWEEKLY = "biweekly", "Bi-weekly"
    MONTHLY = "monthly", "Monthly"


class ChangeSourceChoices(models.TextChoices):
    EMPLOYEE = "employee", "Employee Action"
    ADMIN = "admin", "Admin Action"
    SYSTEM = "system", "System Automated"
