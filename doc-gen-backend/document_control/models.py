import json

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from common.models import BaseModel

User = get_user_model()


class TemplateModel(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='versions')
    version = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    file = models.FileField(upload_to='templates/')

    class Meta:
        ordering = ['-version']
        unique_together = ['parent', 'version']

    def __str__(self):
        if self.parent:
            return f"{self.title} (v{self.version})"
        return f"{self.title} (v{self.version})"

    def get_latest_version(self):
        """Get the latest version of this template"""
        if self.parent:
            return self.parent.versions.order_by('-version').first() or self
        return self.versions.order_by('-version').first() or self

    def get_all_versions(self):
        """Get all versions of this template"""
        if self.parent:
            # Include parent and all its versions
            return TemplateModel.objects.filter(
                Q(id=self.parent.id) | Q(parent=self.parent)
            ).order_by('-version')
        # Include self and all versions
        return TemplateModel.objects.filter(
            Q(id=self.id) | Q(parent=self)
        ).order_by('-version')


class GeneratedDocumentModel(BaseModel):
    """Model to store generated documents along with their inputs for later modification"""
    name = models.CharField(max_length=255, help_text="Name/Title for this generated document")
    template = models.ForeignKey(
        TemplateModel,
        on_delete=models.CASCADE,
        related_name='generated_documents',
        help_text="Template used to generate this document"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_documents',
        help_text="User who generated this document"
    )
    input_data = models.JSONField(
        default=dict,
        help_text="Input data used to generate the document (stored as JSON)"
    )
    generated_file = models.FileField(
        upload_to='generated_documents/',
        help_text="The generated document file"
    )
    export_format = models.CharField(
        max_length=10,
        choices=[('docx', 'DOCX'), ('pdf', 'PDF'), ('doc', 'DOC')],
        default='docx',
        help_text="Format of the generated document"
    )
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('generated', 'Generated'), ('pending_approval', 'Pending Approval'),
                 ('approved', 'Approved'), ('signed', 'Signed')],
        default='generated',
        help_text="Status of the document"
    )
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_documents',
        help_text="User who approved/signed this document"
    )
    approved_at = models.DateTimeField(null=True, blank=True, help_text="When the document was approved/signed")
    signatories_count = models.IntegerField(default=0, help_text="Total number of signatories required")
    signed_count = models.IntegerField(default=0, help_text="Number of signatories who have signed")
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes about this document"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Generated Document'
        verbose_name_plural = 'Generated Documents'

    def __str__(self):
        return f"{self.name} - {self.template.title} ({self.created_at.strftime('%Y-%m-%d')})"

    def get_input_data_display(self):
        """Return formatted input data for display"""
        return json.dumps(self.input_data, indent=2, ensure_ascii=False)

    def is_fully_signed(self):
        """Check if all signatories have signed"""
        return self.signatories_count > 0 and self.signed_count >= self.signatories_count

    def get_pending_signatories(self):
        """Get list of users who still need to sign"""
        return self.signatories.filter(status='pending').select_related('signatory')


class DocumentSignatoryModel(BaseModel):
    """Model to track signatory assignments and signature status for documents"""
    document = models.ForeignKey(
        GeneratedDocumentModel,
        on_delete=models.CASCADE,
        related_name='signatories',
        help_text="Document requiring signature"
    )
    signatory = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='signatory_assignments',
        help_text="User assigned to sign"
    )
    signature_field_name = models.CharField(
        max_length=255,
        help_text="Signature field name (e.g., 'requester_1', 'approver_1')"
    )
    signature_order = models.IntegerField(
        default=0,
        help_text="Order within the field group"
    )
    signed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the signature was applied"
    )
    signature_image = models.ImageField(
        upload_to='signatures/applied/',
        null=True,
        blank=True,
        help_text="Stored signature image after signing"
    )
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('signed', 'Signed')],
        default='pending',
        help_text="Signature status"
    )

    class Meta:
        ordering = ['signature_field_name', 'signature_order']
        verbose_name = 'Document Signatory'
        verbose_name_plural = 'Document Signatories'
        unique_together = ['document', 'signatory', 'signature_field_name', 'signature_order']

    def __str__(self):
        return f"{self.document.name} - {self.signatory.get_full_name()} ({self.signature_field_name})"
