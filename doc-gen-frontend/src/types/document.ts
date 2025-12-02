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
 * Template field definition from parser
 */
export interface TemplateField {
    name: string;
    type: 'text' | 'number' | 'checkbox' | 'signature';
    label: string;
    validation: string;
    options: string[];
    min_value: number | null;
    max_value: number | null;
    is_autofilled: boolean;
    required?: boolean;
}

/**
 * Signature group definition
 */
export interface SignatureGroup {
    prefix: string;
    base_field_name: string;
    name_field: string | null;
    section_label: string;
    signature_fields: TemplateField[];
    is_required: boolean;
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
    fields?: TemplateField[];
    signature_groups?: SignatureGroup[];
}

/**
 * Document form data for state management
 */
export interface DocumentFormData {
    title: string;
    fields: Record<string, any>;
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
 * User model for signatory selection
 */
export interface User {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    full_name: string;
    designation?: string;
    division?: string;
}

/**
 * Signatory assignment
 */
export interface SignatoryAssignment {
    user_id: string;
    signature_field_name: string;
    signature_order: number;
}

/**
 * Create document request
 */
export interface CreateDocumentRequest {
    template_id: string;
    title: string;
    fields: Record<string, any>;
    signatories?: SignatoryAssignment[];
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
