/**
 * API Base URL
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * API Endpoints
 */
export const API_ENDPOINTS = {
    // Auth endpoints
    AUTH: {
        REGISTER: '/api/v1/auth/register/',
        LOGIN: '/api/v1/auth/login/',
        LOGOUT: '/api/v1/auth/logout/',
        REFRESH: '/api/v1/auth/refresh/',
    },
    // User endpoints
    USERS: {
        PROFILE: '/api/v1/users/profile/',
        PROFILE_UPDATE: '/api/v1/users/profile/update/',
        SIGNATURE_UPLOAD: '/api/v1/users/signature/upload/',
        PIN_SETUP: '/api/v1/users/pin/setup/',
        TWO_FA_SETUP: '/api/v1/users/2fa/setup/',
    },
    // Template endpoints
    TEMPLATES: {
        LIST: '/api/v1/templates/',
        DETAIL: (id: string) => `/api/v1/templates/${id}/`,
        VERSIONS: (id: string) => `/api/v1/templates/${id}/versions/`,
        UPLOAD: '/api/v1/templates/upload/',
    },
    // Document endpoints
    DOCUMENTS: {
        LIST: '/api/v1/documents/',
        DETAIL: (id: string) => `/api/v1/documents/${id}/`,
        CREATE: '/api/v1/documents/',
        UPDATE: (id: string) => `/api/v1/documents/${id}/`,
        DELETE: (id: string) => `/api/v1/documents/${id}/`,
        DOWNLOAD: (id: string) => `/api/v1/documents/${id}/download/`,
        PENDING_SIGNATURES: '/api/v1/documents/pending-signatures/',
        APPROVE: (id: string) => `/api/v1/documents/${id}/approve/`,
        GENERATE: (templateId: string) => `/api/v1/document/${templateId}/generate/`,
    },
    // Draft endpoints
    DRAFTS: {
        SAVE: (templateId: string) => `/document/${templateId}/draft/save/`,
        RESTORE: (draftId: string) => `/api/v1/drafts/${draftId}/restore/`,
    },
} as const;

/**
 * Application Routes
 */
export const ROUTES = {
    // Public routes
    LOGIN: '/login',
    REGISTER: '/register',
    // Protected routes
    HOME: '/',
    PROFILE: '/profile',
    // Template routes
    TEMPLATES: '/templates',
    TEMPLATE_DETAIL: (id: string) => `/templates/${id}`,
    // Document routes
    DOCUMENTS: '/documents',
    DOCUMENTS_NEW: '/documents/new',
    DOCUMENTS_EDIT: (id: string) => `/documents/${id}/edit`,
    DOCUMENTS_PENDING_SIGNATURES: '/documents/pending-signatures',
} as const;

