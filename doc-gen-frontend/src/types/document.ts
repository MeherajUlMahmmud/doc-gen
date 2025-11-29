/**
 * Document status enum
 */
export enum DocumentStatus {
    DRAFT = 'draft',
    PENDING = 'pending_signature',
    APPROVED = 'approved',
    REJECTED = 'rejected',
}

/**
 * Template model
 */
export interface Template {
    id: string;
    title: string;
    description?: string;
    file: string;
    version: number;
    is_active: boolean;
    created_by: string;
    created_at: string;
    updated_at: string;
}

/**
 * Document field type
 */
export interface DocumentField {
    name: string;
    value: string | number | boolean;
    field_type: 'text' | 'number' | 'checkbox' | 'signature';
    label?: string;
}

/**
 * Document model
 */
export interface Document {
    id: string;
    template: Template;
    template_id: string;
    title: string;
    status: DocumentStatus;
    fields: Record<string, any>;
    generated_file?: string;
    created_by: string;
    created_at: string;
    updated_at: string;
    approved_by?: string;
    approved_at?: string;
}

/**
 * Document draft
 */
export interface DocumentDraft {
    id: string;
    template: Template;
    template_id: string;
    fields: Record<string, any>;
    created_at: string;
    updated_at: string;
}

/**
 * Create document request
 */
export interface CreateDocumentRequest {
    template_id: string;
    title: string;
    fields: Record<string, any>;
}

/**
 * Update document request
 */
export interface UpdateDocumentRequest {
    title?: string;
    fields?: Record<string, any>;
}

/**
 * Approve document request
 */
export interface ApproveDocumentRequest {
    pin: string;
    totp_code?: string;
}

/**
 * Template list response
 */
export interface TemplateListResponse {
    templates: Template[];
    total: number;
}

/**
 * Document list response
 */
export interface DocumentListResponse {
    documents: Document[];
    total: number;
}

/**
 * Document filters
 */
export interface DocumentFilters {
    status?: DocumentStatus;
    search?: string;
    page?: number;
    page_size?: number;
}

/**
 * Template filters
 */
export interface TemplateFilters {
    search?: string;
    is_active?: boolean;
    page?: number;
    page_size?: number;
}
