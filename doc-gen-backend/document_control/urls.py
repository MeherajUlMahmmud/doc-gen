from django.urls import path

from .views import (
    TemplatesListAPIView,
    TemplateDetailAPIView,
    TemplateVersionsAPIView,
    TemplateUploadAPIView,
    TemplateDownloadAPIView,
    TemplatePreviewAPIView,
    DocumentsListAPIView,
    DocumentCreateAPIView,
    DocumentDetailAPIView,
    DocumentDeleteAPIView,
    DocumentDownloadAPIView,
    PendingSignaturesAPIView,
    ApproveDocumentAPIView,
    UsersListAPIView,
)

urlpatterns = [
    # Templates
    path('api/v1/templates/', TemplatesListAPIView.as_view(), name='templates_list_api'),
    path('api/v1/templates/upload/', TemplateUploadAPIView.as_view(), name='template_upload_api'),
    path('api/v1/templates/<uuid:pk>/', TemplateDetailAPIView.as_view(), name='template_detail_api'),
    path('api/v1/templates/<uuid:pk>/versions/', TemplateVersionsAPIView.as_view(), name='template_versions_api'),
    path('api/v1/templates/<uuid:pk>/download/', TemplateDownloadAPIView.as_view(), name='template_download_api'),
    path('api/v1/templates/<uuid:pk>/preview/', TemplatePreviewAPIView.as_view(), name='template_preview_api'),

    # Documents
    path('api/v1/documents/', DocumentsListAPIView.as_view(), name='documents_list_api'),
    path('api/v1/documents/create/', DocumentCreateAPIView.as_view(), name='document_create_api'),
    path('api/v1/documents/<uuid:pk>/', DocumentDetailAPIView.as_view(), name='document_detail_api'),
    path('api/v1/documents/<uuid:pk>/delete/', DocumentDeleteAPIView.as_view(), name='document_delete_api'),
    path('api/v1/documents/<uuid:pk>/download/', DocumentDownloadAPIView.as_view(), name='document_download_api'),

    # Pending signatures
    path('api/v1/documents/pending-signatures/', PendingSignaturesAPIView.as_view(), name='pending_signatures_api'),

    # Document approval
    path('api/v1/documents/<uuid:pk>/approve/', ApproveDocumentAPIView.as_view(), name='approve_document_api'),

    # Users list for signatory selection
    path('api/v1/users/', UsersListAPIView.as_view(), name='users_list_api'),
]
