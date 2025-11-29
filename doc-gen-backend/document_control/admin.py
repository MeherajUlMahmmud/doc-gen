from django.contrib import admin

from document_control.models import TemplateModel, GeneratedDocumentModel, DocumentSignatoryModel


@admin.register(TemplateModel)
class TemplateModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'version', 'parent', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'get_latest_version_display', 'get_all_versions_display')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'parent', 'version', 'is_active')
        }),
        ('File', {
            'fields': ('file',)
        }),
        ('Version Information', {
            'fields': ('get_latest_version_display', 'get_all_versions_display'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_latest_version_display(self, obj):
        """Display the latest version of this template"""
        if obj:
            latest = obj.get_latest_version()
            if latest and latest.id != obj.id:
                return f"Latest: {latest.title} (v{latest.version})"
            return f"Current: {obj.title} (v{obj.version})"
        return "-"

    get_latest_version_display.short_description = "Latest Version"

    def get_all_versions_display(self, obj):
        """Display all versions of this template"""
        if obj:
            versions = obj.get_all_versions()
            version_list = [f"v{v.version}" for v in versions]
            return ", ".join(version_list) if version_list else "No versions"
        return "-"

    get_all_versions_display.short_description = "All Versions"


@admin.register(GeneratedDocumentModel)
class GeneratedDocumentModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'template', 'user', 'export_format', 'created_at', 'updated_at')
    list_filter = ('export_format', 'created_at', 'template')
    search_fields = ('name', 'template__title', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'get_input_data_display')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template', 'user', 'export_format', 'notes')
        }),
        ('Document', {
            'fields': ('generated_file',)
        }),
        ('Input Data', {
            'fields': ('get_input_data_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_input_data_display(self, obj):
        """Display formatted input data"""
        if obj:
            return obj.get_input_data_display()
        return "-"

    get_input_data_display.short_description = "Input Data"


@admin.register(DocumentSignatoryModel)
class DocumentSignatoryAdmin(admin.ModelAdmin):
    list_display = ('document', 'signatory', 'signature_field_name', 'status', 'signed_at', 'created_at')
    list_filter = ('status', 'signature_field_name', 'created_at', 'signed_at')
    search_fields = ('document__name', 'signatory__email', 'signatory__first_name', 'signatory__last_name',
                     'signature_field_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('document', 'signatory', 'signature_field_name', 'signature_order', 'status')
        }),
        ('Signature', {
            'fields': ('signature_image', 'signed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
