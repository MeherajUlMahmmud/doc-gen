import api, { handleApiResponse } from './api';
import type { ApiResponse } from '@/types/api';
import type {
    Template,
    Document,
    CreateDocumentRequest,
    UpdateDocumentRequest,
    ApproveDocumentRequest,
    TemplateFilters,
    DocumentFilters,
} from '@/types/document';
import { API_ENDPOINTS } from '@/constants/urls';

/**
 * Document service for document and template-related API calls
 */
export const documentService = {
    /**
     * Get all templates
     */
    async getTemplates(filters?: TemplateFilters): Promise<{ data: Template[]; total: number }> {
        const params = new URLSearchParams();

        if (filters?.search) params.append('search', filters.search);
        if (filters?.is_active !== undefined) params.append('is_active', String(filters.is_active));
        if (filters?.page) params.append('page', String(filters.page));
        if (filters?.page_size) params.append('page_size', String(filters.page_size));

        const response = await api.get<ApiResponse<Template[]>>(
            `${API_ENDPOINTS.TEMPLATES.LIST}?${params.toString()}`
        );

        return {
            data: response.data.data || [],
            total: response.data.meta?.total_records || 0,
        };
    },

    /**
     * Get template by ID
     */
    async getTemplate(id: string): Promise<Template> {
        const response = await api.get<ApiResponse<Template>>(API_ENDPOINTS.TEMPLATES.DETAIL(id));
        return handleApiResponse(response.data);
    },

    /**
     * Get all versions of a template by ID
     */
    async getTemplateVersions(id: string): Promise<Template[]> {
        const response = await api.get<ApiResponse<Template[]>>(API_ENDPOINTS.TEMPLATES.VERSIONS(id));
        return handleApiResponse(response.data);
    },

    /**
     * Upload a new template
     */
    async uploadTemplate(formData: FormData): Promise<Template> {
        const response = await api.post<ApiResponse<Template>>(
            API_ENDPOINTS.TEMPLATES.UPLOAD,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }
        );
        return handleApiResponse(response.data);
    },

    /**
     * Get all documents for current user
     */
    async getDocuments(filters?: DocumentFilters): Promise<{ data: Document[]; total: number }> {
        const params = new URLSearchParams();

        if (filters?.status) params.append('status', filters.status);
        if (filters?.search) params.append('search', filters.search);
        if (filters?.page) params.append('page', String(filters.page));
        if (filters?.page_size) params.append('page_size', String(filters.page_size));

        const response = await api.get<ApiResponse<Document[]>>(
            `${API_ENDPOINTS.DOCUMENTS.LIST}?${params.toString()}`
        );

        return {
            data: response.data.data || [],
            total: response.data.meta?.total_records || 0,
        };
    },

    /**
     * Get document by ID
     */
    async getDocument(id: string): Promise<Document> {
        const response = await api.get<ApiResponse<Document>>(API_ENDPOINTS.DOCUMENTS.DETAIL(id));
        return handleApiResponse(response.data);
    },

    /**
     * Create a new document
     */
    async createDocument(data: CreateDocumentRequest): Promise<Document> {
        const response = await api.post<ApiResponse<Document>>(API_ENDPOINTS.DOCUMENTS.CREATE, data);
        return handleApiResponse(response.data);
    },

    /**
     * Update document
     */
    async updateDocument(id: string, data: UpdateDocumentRequest): Promise<Document> {
        const response = await api.patch<ApiResponse<Document>>(API_ENDPOINTS.DOCUMENTS.UPDATE(id), data);
        return handleApiResponse(response.data);
    },

    /**
     * Delete document
     */
    async deleteDocument(id: string): Promise<void> {
        const response = await api.delete<ApiResponse<void>>(API_ENDPOINTS.DOCUMENTS.DELETE(id));
        return handleApiResponse(response.data);
    },

    /**
     * Download document
     */
    async downloadDocument(id: string): Promise<Blob> {
        const response = await api.get(API_ENDPOINTS.DOCUMENTS.DOWNLOAD(id), {
            responseType: 'blob',
        });
        return response.data;
    },

    /**
     * Get documents pending signature for current user
     */
    async getPendingSignatures(): Promise<Document[]> {
        const response = await api.get<ApiResponse<Document[]>>(API_ENDPOINTS.DOCUMENTS.PENDING_SIGNATURES);
        return handleApiResponse(response.data);
    },

    /**
     * Approve/sign a document
     */
    async approveDocument(id: string, data: ApproveDocumentRequest): Promise<Document> {
        const response = await api.post<ApiResponse<Document>>(
            API_ENDPOINTS.DOCUMENTS.APPROVE(id),
            data
        );
        return handleApiResponse(response.data);
    },

    /**
     * Generate document from template
     */
    async generateDocument(templateId: string, fields: Record<string, any>): Promise<Document> {
        const response = await api.post<ApiResponse<Document>>(
            API_ENDPOINTS.DOCUMENTS.GENERATE(templateId),
            { fields }
        );
        return handleApiResponse(response.data);
    },

    /**
     * Save document as draft
     */
    async saveDraft(templateId: string, fields: Record<string, any>): Promise<void> {
        const response = await api.post<ApiResponse<void>>(
            API_ENDPOINTS.DRAFTS.SAVE(templateId),
            { fields }
        );
        return handleApiResponse(response.data);
    },

    /**
     * Restore draft
     */
    async restoreDraft(draftId: string): Promise<Record<string, any>> {
        const response = await api.post<ApiResponse<Record<string, any>>>(
            API_ENDPOINTS.DRAFTS.RESTORE(draftId)
        );
        return handleApiResponse(response.data);
    },
};
