from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from document_control.constants import SignatoryErrorMessages
from document_control.models import GeneratedDocumentModel, DocumentSignatoryModel
from document_control.serializers.generated_document import GeneratedDocumentModelSerializer
from user_control.models import UserModel
from user_control.serializers.user import UserModelSerializer


class DocumentSignatoryModelSerializerMeta(ModelSerializer):
    """Base meta class for DocumentSignatoryModel serializers"""
    signatory = UserModelSerializer(read_only=True)
    document = GeneratedDocumentModelSerializer.Lite(read_only=True)

    class Meta:
        model = DocumentSignatoryModel
        ref_name = 'DocumentSignatoryModelSerializer'
        fields = [
            'id',
            'document',
            'signatory',
            'signature_field_name',
            'signature_order',
            'status',
            'signed_at',
            'signature_image',
            'created_at',
            'updated_at',
        ]


class DocumentSignatoryModelSerializer:
    class List(DocumentSignatoryModelSerializerMeta):
        """Serializer for listing signatories"""

        class Meta(DocumentSignatoryModelSerializerMeta.Meta):
            fields = [
                'id',
                'signatory',
                'signature_field_name',
                'signature_order',
                'status',
                'signed_at',
                'created_at',
            ]

    class Lite(DocumentSignatoryModelSerializerMeta):
        """Lightweight serializer for signatory references"""

        class Meta(DocumentSignatoryModelSerializerMeta.Meta):
            fields = [
                'id',
                'signatory',
                'status',
                'signed_at',
            ]

    class Info(DocumentSignatoryModelSerializerMeta):
        """Minimal signatory information"""

        class Meta(DocumentSignatoryModelSerializerMeta.Meta):
            fields = [
                'id',
                'signatory',
                'signature_field_name',
                'status',
            ]

    class Detail(DocumentSignatoryModelSerializerMeta):
        """Detailed signatory information"""

        class Meta(DocumentSignatoryModelSerializerMeta.Meta):
            fields = DocumentSignatoryModelSerializerMeta.Meta.fields + [
            ]

    class Create(DocumentSignatoryModelSerializerMeta):
        """Serializer for creating signatories"""
        document = serializers.PrimaryKeyRelatedField(
            write_only=True,
            required=True,
            queryset=GeneratedDocumentModel.objects.all(),
            help_text="Document ID",
            error_messages={
                'required': SignatoryErrorMessages.SIGNATORY_REQUIRED,
            }
        )
        signatory = serializers.PrimaryKeyRelatedField(
            write_only=True,
            required=True,
            queryset=UserModel.objects.all(),
            help_text="Signatory user ID",
            error_messages={
                'required': SignatoryErrorMessages.SIGNATORY_REQUIRED,
            }
        )
        signature_field_name = CharField(
            write_only=True,
            required=True,
            max_length=255,
            help_text="Signature field name (e.g., 'requester_1', 'approver_1')",
            error_messages={
                'required': SignatoryErrorMessages.SIGNATURE_FIELD_REQUIRED,
                'max_length': SignatoryErrorMessages.SIGNATURE_FIELD_MAX_LENGTH,
            }
        )
        signature_order = serializers.IntegerField(
            write_only=True,
            required=True,
            min_value=0,
            help_text="Order within the field group",
            error_messages={
                'required': SignatoryErrorMessages.SIGNATURE_ORDER_INVALID,
            }
        )

        class Meta(DocumentSignatoryModelSerializerMeta.Meta):
            fields = [
                'document',
                'signatory',
                'signature_field_name',
                'signature_order',
            ]

        def validate_signature_field_name(self, value):
            """Validate signature field name"""
            if not value or len(value.strip()) == 0:
                raise serializers.ValidationError(SignatoryErrorMessages.SIGNATURE_FIELD_REQUIRED)
            if len(value) > 255:
                raise serializers.ValidationError(SignatoryErrorMessages.SIGNATURE_FIELD_MAX_LENGTH)
            return value.strip()

        def validate(self, data):
            """Cross-field validation"""
            document = data.get('document')
            signatory = data.get('signatory')
            signature_field_name = data.get('signature_field_name')
            signature_order = data.get('signature_order')

            # Check for duplicate signatory assignment
            if document and signatory and signature_field_name and signature_order is not None:
                existing = DocumentSignatoryModel.objects.filter(
                    document=document,
                    signatory=signatory,
                    signature_field_name=signature_field_name,
                    signature_order=signature_order
                ).exists()
                if existing:
                    raise serializers.ValidationError(
                        "This signatory is already assigned to this signature field."
                    )

            return data

        def create(self, validated_data):
            """Create signatory"""
            try:
                signatory = DocumentSignatoryModel.objects.create(
                    status='pending',
                    **validated_data
                )
                # Update document signatories count
                document = validated_data['document']
                document.signatories_count = document.signatories.count()
                document.save()
                return signatory
            except Exception as e:
                raise serializers.ValidationError(
                    f"Failed to create signatory: {str(e)}"
                )

    class Update(DocumentSignatoryModelSerializerMeta):
        """Serializer for updating signatories"""
        signature_order = serializers.IntegerField(
            write_only=True,
            required=False,
            min_value=0,
            help_text="Order within the field group",
            error_messages={
                'min_value': SignatoryErrorMessages.SIGNATURE_ORDER_INVALID,
            }
        )

        class Meta(DocumentSignatoryModelSerializerMeta.Meta):
            fields = [
                'signature_order',
            ]

    class UpdateStatus(serializers.Serializer):
        """Serializer for updating signatory status"""
        status = CharField(
            required=True,
            max_length=20,
            help_text="Signatory status: pending or signed",
            error_messages={
                'required': SignatoryErrorMessages.STATUS_INVALID,
                'max_length': SignatoryErrorMessages.STATUS_INVALID,
            }
        )

        def validate_status(self, value):
            """Validate status"""
            valid_statuses = ['pending', 'signed']
            if value not in valid_statuses:
                raise serializers.ValidationError(SignatoryErrorMessages.STATUS_INVALID)
            return value
