from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from document_control.constants import DocumentErrorMessages
from document_control.models import GeneratedDocumentModel, TemplateModel
from document_control.serializers.template import TemplateModelSerializer
from user_control.serializers.user import UserModelSerializer


class GeneratedDocumentModelSerializerMeta(ModelSerializer):
    """Base meta class for GeneratedDocumentModel serializers"""
    user = UserModelSerializer(read_only=True)
    template = TemplateModelSerializer.Lite(read_only=True)
    signatories = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedDocumentModel
        ref_name = 'GeneratedDocumentModelSerializer'
        fields = [
            'id',
            'name',
            'template',
            'user',
            'status',
            'input_data',
            'generated_file',
            'file_url',
            'export_format',
            'approver',
            'approved_at',
            'signatories_count',
            'signed_count',
            'notes',
            'created_at',
            'updated_at',
            'signatories',
        ]

    def get_signatories(self, obj):
        """Get signatories for the document"""
        signatories = obj.signatories.all()
        
        from document_control.serializers.document_signatory import DocumentSignatoryModelSerializer
        # Use the List serializer class defined later in the file
        return DocumentSignatoryModelSerializer.List(signatories, many=True, context=self.context).data

    def get_file_url(self, obj):
        """Get file URL"""
        if obj.generated_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.generated_file.url)
            return obj.generated_file.url
        return None


class GeneratedDocumentModelSerializer:
    class List(GeneratedDocumentModelSerializerMeta):
        """Serializer for listing documents"""

        class Meta(GeneratedDocumentModelSerializerMeta.Meta):
            fields = [
                'id',
                'name',
                'template',
                'user',
                'status',
                'file_url',
                'signatories_count',
                'signed_count',
                'created_at',
                'updated_at',
            ]

    class Lite(GeneratedDocumentModelSerializerMeta):
        """Lightweight serializer for document references"""

        class Meta(GeneratedDocumentModelSerializerMeta.Meta):
            fields = [
                'id',
                'name',
                'status',
                'created_at',
            ]

    class Info(GeneratedDocumentModelSerializerMeta):
        """Minimal document information"""

        class Meta(GeneratedDocumentModelSerializerMeta.Meta):
            fields = [
                'id',
                'name',
                'template',
                'status',
                'file_url',
                'created_at',
            ]

    class Detail(GeneratedDocumentModelSerializerMeta):
        """Detailed document information"""

        class Meta(GeneratedDocumentModelSerializerMeta.Meta):
            fields = GeneratedDocumentModelSerializerMeta.Meta.fields + [
            ]

    class Create(GeneratedDocumentModelSerializerMeta):
        """Serializer for creating documents"""
        name = CharField(
            write_only=True,
            required=True,
            max_length=255,
            min_length=2,
            help_text="Document name must be between 2 and 255 characters",
            error_messages={
                'required': DocumentErrorMessages.NAME_REQUIRED,
                'min_length': DocumentErrorMessages.NAME_MIN_LENGTH,
                'max_length': DocumentErrorMessages.NAME_MAX_LENGTH,
            }
        )
        template = serializers.PrimaryKeyRelatedField(
            write_only=True,
            required=True,
            queryset=TemplateModel.objects.filter(is_active=True),
            help_text="Template ID",
            error_messages={
                'required': DocumentErrorMessages.TEMPLATE_REQUIRED,
            }
        )
        input_data = serializers.JSONField(
            write_only=True,
            required=True,
            help_text="Input data for document generation (JSON format)",
            error_messages={
                'required': DocumentErrorMessages.INPUT_DATA_REQUIRED,
            }
        )
        export_format = CharField(
            write_only=True,
            required=False,
            max_length=10,
            help_text="Export format: docx, pdf, or doc",
            error_messages={
                'max_length': DocumentErrorMessages.EXPORT_FORMAT_INVALID,
            }
        )
        notes = CharField(
            write_only=True,
            required=False,
            allow_blank=True,
            max_length=5000,
            help_text="Optional notes about the document",
            error_messages={
                'max_length': DocumentErrorMessages.NOTES_MAX_LENGTH,
            }
        )

        class Meta(GeneratedDocumentModelSerializerMeta.Meta):
            fields = [
                'name',
                'template',
                'input_data',
                'export_format',
                'notes',
            ]

        def validate_name(self, value):
            """Validate document name"""
            if not value or len(value.strip()) < 2:
                raise serializers.ValidationError(DocumentErrorMessages.NAME_MIN_LENGTH)
            if len(value) > 255:
                raise serializers.ValidationError(DocumentErrorMessages.NAME_MAX_LENGTH)
            return value.strip()

        def validate_template(self, value):
            """Validate template"""
            if not value:
                raise serializers.ValidationError(DocumentErrorMessages.TEMPLATE_REQUIRED)
            if not value.is_active:
                raise serializers.ValidationError(DocumentErrorMessages.TEMPLATE_INACTIVE)
            return value

        def validate_input_data(self, value):
            """Validate input data"""
            if not value:
                raise serializers.ValidationError(DocumentErrorMessages.INPUT_DATA_REQUIRED)
            if not isinstance(value, dict):
                raise serializers.ValidationError(DocumentErrorMessages.INPUT_DATA_INVALID)
            return value

        def validate_export_format(self, value):
            """Validate export format"""
            if value and value not in ['docx', 'pdf', 'doc']:
                raise serializers.ValidationError(DocumentErrorMessages.EXPORT_FORMAT_INVALID)
            return value or 'docx'

        def validate(self, data):
            """Cross-field validation"""
            template = data.get('template')
            if template and not template.is_active:
                raise serializers.ValidationError({
                    'template': DocumentErrorMessages.TEMPLATE_INACTIVE
                })
            return data

        def create(self, validated_data):
            """Create document"""
            try:
                user = self.context['request'].user
                document = GeneratedDocumentModel.objects.create(
                    user=user,
                    status='draft',
                    **validated_data
                )
                return document
            except Exception as e:
                raise serializers.ValidationError(
                    f"Failed to create document: {str(e)}"
                )

    class Update(GeneratedDocumentModelSerializerMeta):
        """Serializer for updating documents"""
        name = CharField(
            write_only=True,
            required=False,
            max_length=255,
            min_length=2,
            help_text="Document name must be between 2 and 255 characters",
            error_messages={
                'min_length': DocumentErrorMessages.NAME_MIN_LENGTH,
                'max_length': DocumentErrorMessages.NAME_MAX_LENGTH,
            }
        )
        notes = CharField(
            write_only=True,
            required=False,
            allow_blank=True,
            max_length=5000,
            help_text="Optional notes about the document",
            error_messages={
                'max_length': DocumentErrorMessages.NOTES_MAX_LENGTH,
            }
        )

        class Meta(GeneratedDocumentModelSerializerMeta.Meta):
            fields = [
                'name',
                'notes',
            ]

        def validate_name(self, value):
            """Validate document name"""
            if value and len(value.strip()) < 2:
                raise serializers.ValidationError(DocumentErrorMessages.NAME_MIN_LENGTH)
            if value and len(value) > 255:
                raise serializers.ValidationError(DocumentErrorMessages.NAME_MAX_LENGTH)
            return value.strip() if value else value

    class UpdateStatus(serializers.Serializer):
        """Serializer for updating document status"""
        status = CharField(
            required=True,
            max_length=20,
            help_text="Document status: draft, generated, pending_approval, approved, signed",
            error_messages={
                'required': DocumentErrorMessages.STATUS_INVALID,
                'max_length': DocumentErrorMessages.STATUS_INVALID,
            }
        )

        def validate_status(self, value):
            """Validate status"""
            valid_statuses = ['draft', 'generated', 'pending_approval', 'approved', 'signed']
            if value not in valid_statuses:
                raise serializers.ValidationError(DocumentErrorMessages.STATUS_INVALID)
            return value

    class Approve(GeneratedDocumentModelSerializerMeta):
        """Serializer for approving/signing documents"""
        pin = CharField(
            write_only=True,
            required=True,
            min_length=4,
            max_length=20,
            help_text="PIN to verify signature authorization",
            error_messages={
                'required': 'PIN is required',
                'min_length': 'PIN must be at least 4 characters',
                'max_length': 'PIN must be at most 20 characters',
            }
        )
        totp_code = CharField(
            write_only=True,
            required=False,
            min_length=6,
            max_length=6,
            help_text="TOTP code for 2FA verification (required if 2FA is enabled)",
            error_messages={
                'min_length': 'TOTP code must be 6 digits',
                'max_length': 'TOTP code must be 6 digits',
            }
        )

        class Meta(GeneratedDocumentModelSerializerMeta.Meta):
            fields = GeneratedDocumentModelSerializerMeta.Meta.fields

        def validate_pin(self, value):
            """Validate PIN format"""
            if not value or len(value.strip()) < 4:
                raise serializers.ValidationError('PIN must be at least 4 characters')
            return value.strip()

        def validate_totp_code(self, value):
            """Validate TOTP code format"""
            if value and (len(value) != 6 or not value.isdigit()):
                raise serializers.ValidationError('TOTP code must be 6 digits')
            return value

        def validate(self, data):
            """Cross-field validation"""
            user = self.context['request'].user
            
            # Check if 2FA is enabled and totp_code is provided
            if user.two_factor_enabled and not data.get('totp_code'):
                raise serializers.ValidationError({
                    'totp_code': '2FA code is required when 2FA is enabled'
                })
            
            return data
