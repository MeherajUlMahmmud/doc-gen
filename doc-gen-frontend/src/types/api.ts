/**
 * Standard API response structure from Django backend
 */
export interface ApiResponse<T = any> {
    status: 'success' | 'error';
    status_code: number;
    message?: string;
    data?: T;
    errors?: any;
    meta?: PaginationMeta;
}

/**
 * Pagination metadata for list endpoints
 */
export interface PaginationMeta {
    prev_page?: string | null;
    next_page?: string | null;
    total_pages?: number;
    total_records?: number;
}

/**
 * API error response
 */
export interface ApiError {
    message: string;
    errors?: Record<string, string[]>;
    status_code?: number;
}
