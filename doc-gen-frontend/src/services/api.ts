import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type { ApiResponse, ApiError } from '@/types/api';
import { API_BASE_URL, API_ENDPOINTS, ROUTES } from '@/constants/urls';

// Create axios instance with base configuration
const api: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Request interceptor - Add auth token to requests
 */
api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('access_token');

        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

/**
 * Response interceptor - Handle errors and token refresh
 */
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error: AxiosError<ApiResponse>) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & {
            _retry?: boolean;
        };

        // If error is 401 and we haven't retried yet, try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            const refreshToken = localStorage.getItem('refresh_token');

            if (refreshToken) {
                try {
                    // Try to refresh the access token
                    const response = await axios.post<ApiResponse<{ access: string }>>(
                        `${API_BASE_URL}${API_ENDPOINTS.AUTH.REFRESH}`,
                        { refresh: refreshToken }
                    );

                    const newAccessToken = response.data.data?.access;

                    if (newAccessToken) {
                        // Update stored token
                        localStorage.setItem('access_token', newAccessToken);

                        // Update the failed request with new token
                        if (originalRequest.headers) {
                            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                        }

                        // Retry the original request
                        return api(originalRequest);
                    }
                } catch (refreshError) {
                    // Refresh failed - clear tokens and redirect to login
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('user');

                    window.location.href = ROUTES.LOGIN;
                    return Promise.reject(refreshError);
                }
            } else {
                // No refresh token - redirect to login
                window.location.href = ROUTES.LOGIN;
            }
        }

        // Transform error to our ApiError format
        const apiError: ApiError = {
            message: error.response?.data?.message || error.message || 'An unexpected error occurred',
            errors: error.response?.data?.errors,
            status_code: error.response?.status,
        };

        return Promise.reject(apiError);
    }
);

export default api;

/**
 * Helper function to handle API responses
 */
export const handleApiResponse = <T>(response: ApiResponse<T>): T => {
    if (response.status === 'success' && response.data) {
        return response.data;
    }

    throw new Error(response.message || 'Request failed');
};

/**
 * Helper function to extract error message from API error
 */
export const getErrorMessage = (error: unknown): string => {
    if (error && typeof error === 'object' && 'message' in error) {
        return (error as ApiError).message;
    }

    if (typeof error === 'string') {
        return error;
    }

    return 'An unexpected error occurred';
};
