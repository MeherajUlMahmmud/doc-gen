from rest_framework import serializers
from rest_framework.fields import CharField, FileField
from rest_framework.serializers import ModelSerializer

from document_control.constants import TemplateErrorMessages
from document_control.models import TemplateModel


class TemplateModelSerializerMeta(ModelSerializer):
    """Base meta class for TemplateModel serializers"""

    class Meta:
        model = TemplateModel
        ref_name = 'TemplateModelSerializer'
        fields = [
            'id',
            'title',
            'description',
            'version',
            'is_active',
            'parent',
            'file',
            'created_at',
            'updated_at',
        ]


class TemplateModelSerializer:
    class List(TemplateModelSerializerMeta):
        """Serializer for listing templates"""

        class Meta(TemplateModelSerializerMeta.Meta):
            fields = TemplateModelSerializerMeta.Meta.fields + [
                'created_at',
            ]

    class Lite(TemplateModelSerializerMeta):
        """Lightweight serializer for template references"""

        class Meta(TemplateModelSerializerMeta.Meta):
            fields = [
                'id',
                'title',
                'version',
                'is_active',
            ]

    class Info(TemplateModelSerializerMeta):
        """Minimal template information"""

        class Meta(TemplateModelSerializerMeta.Meta):
            fields = [
                'id',
                'title',
                'description',
                'version',
                'is_active',
            ]

    class Detail(TemplateModelSerializerMeta):
        """Detailed template information"""

        class Meta(TemplateModelSerializerMeta.Meta):
            fields = TemplateModelSerializerMeta.Meta.fields + [
            ]

    class Create(TemplateModelSerializerMeta):
        """Serializer for creating templates"""
        title = CharField(
            write_only=True,
            required=True,
            max_length=255,
            min_length=2,
            help_text="Template title must be between 2 and 255 characters",
            error_messages={
                'required': TemplateErrorMessages.TITLE_REQUIRED,
                'min_length': TemplateErrorMessages.TITLE_MIN_LENGTH,
                'max_length': TemplateErrorMessages.TITLE_MAX_LENGTH,
            }
        )
        description = CharField(
            write_only=True,
            required=False,
            allow_blank=True,
            max_length=5000,
            help_text="Template description (optional)",
            error_messages={
                'max_length': TemplateErrorMessages.DESCRIPTION_MAX_LENGTH,
            }
        )
        file = FileField(
            write_only=True,
            required=True,
            help_text="Template file (.docx format)",
            error_messages={
                'required': TemplateErrorMessages.FILE_REQUIRED,
            }
        )
        upload_type = CharField(
            write_only=True,
            required=True,
            help_text="Upload type: 'new' or 'version'",
            error_messages={
                'required': 'Upload type is required',
            }
        )
        parent_template_id = CharField(
            write_only=True,
            required=False,
            allow_null=True,
            help_text="Parent template ID (required when upload_type is 'version')",
        )

        class Meta(TemplateModelSerializerMeta.Meta):
            fields = [
                'title',
                'description',
                'file',
                'upload_type',
                'parent_template_id',
            ]

        def validate_title(self, value):
            """Validate title"""
            if not value or len(value.strip()) < 2:
                raise serializers.ValidationError(TemplateErrorMessages.TITLE_MIN_LENGTH)
            if len(value) > 255:
                raise serializers.ValidationError(TemplateErrorMessages.TITLE_MAX_LENGTH)
            return value.strip()

        def validate_file(self, value):
            """Validate file type and size"""
            if not value:
                raise serializers.ValidationError(TemplateErrorMessages.FILE_REQUIRED)

            # Check file extension
            if not value.name.endswith('.docx'):
                raise serializers.ValidationError(TemplateErrorMessages.FILE_INVALID_TYPE)

            # Check file size (10MB max)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError(TemplateErrorMessages.FILE_SIZE_EXCEEDED)

            return value

        def validate_upload_type(self, value):
            """Validate upload type"""
            if value not in ['new', 'version']:
                raise serializers.ValidationError("Upload type must be either 'new' or 'version'")
            return value

        def validate(self, attrs):
            """Cross-field validation"""
            upload_type = attrs.get('upload_type')
            parent_template_id = attrs.get('parent_template_id')

            # If upload_type is 'version', parent_template_id is required
            if upload_type == 'version' and not parent_template_id:
                raise serializers.ValidationError({
                    'parent_template_id': 'Parent template is required when uploading a new version'
                })

            # If upload_type is 'new', parent_template_id should not be provided
            if upload_type == 'new' and parent_template_id:
                raise serializers.ValidationError({
                    'parent_template_id': 'Parent template should not be provided when uploading a new template'
                })

            # Validate that parent template exists if provided
            if parent_template_id:
                try:
                    parent = TemplateModel.objects.get(id=parent_template_id, is_active=True)
                    # Ensure parent is not itself a child
                    if parent.parent is not None:
                        raise serializers.ValidationError({
                            'parent_template_id': 'You must select the original template, not a version'
                        })
                except TemplateModel.DoesNotExist:
                    raise serializers.ValidationError({
                        'parent_template_id': 'Parent template not found or is inactive'
                    })

            return attrs

    class Update(TemplateModelSerializerMeta):
        """Serializer for updating templates"""
        title = CharField(
            write_only=True,
            required=False,
            max_length=255,
            min_length=2,
            help_text="Template title must be between 2 and 255 characters",
            error_messages={
                'min_length': TemplateErrorMessages.TITLE_MIN_LENGTH,
                'max_length': TemplateErrorMessages.TITLE_MAX_LENGTH,
            }
        )
        description = CharField(
            write_only=True,
            required=False,
            allow_blank=True,
            max_length=5000,
            help_text="Template description (optional)",
            error_messages={
                'max_length': TemplateErrorMessages.DESCRIPTION_MAX_LENGTH,
            }
        )
        is_active = serializers.BooleanField(
            required=False,
            help_text="Set template active status"
        )

        class Meta(TemplateModelSerializerMeta.Meta):
            fields = [
                'title',
                'description',
                'is_active',
            ]

        def validate_title(self, value):
            """Validate title"""
            if value and len(value.strip()) < 2:
                raise serializers.ValidationError(TemplateErrorMessages.TITLE_MIN_LENGTH)
            if value and len(value) > 255:
                raise serializers.ValidationError(TemplateErrorMessages.TITLE_MAX_LENGTH)
            return value.strip() if value else value
