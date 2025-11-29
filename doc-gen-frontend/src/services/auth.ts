import api, { handleApiResponse } from './api';
import type { ApiResponse } from '@/types/api';
import type {
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    LogoutRequest,
} from '@/types/auth';
import { API_ENDPOINTS } from '@/constants/urls';

/**
 * Auth service for authentication-related API calls
 */
export const authService = {
    /**
     * Register a new user
     */
    async register(data: RegisterRequest): Promise<RegisterResponse> {
        const response = await api.post<ApiResponse<RegisterResponse>>(
            API_ENDPOINTS.AUTH.REGISTER,
            data
        );
        return handleApiResponse(response.data);
    },

    /**
     * Login user and get JWT tokens
     */
    async login(data: LoginRequest): Promise<LoginResponse> {
        const response = await api.post<ApiResponse<LoginResponse>>(
            API_ENDPOINTS.AUTH.LOGIN,
            data
        );
        return handleApiResponse(response.data);
    },

    /**
     * Logout user and blacklist refresh token
     */
    async logout(data: LogoutRequest): Promise<void> {
        const response = await api.post<ApiResponse<void>>(
            API_ENDPOINTS.AUTH.LOGOUT,
            data
        );
        return handleApiResponse(response.data);
    },

    /**
     * Refresh access token using refresh token
     */
    async refreshToken(refreshToken: string): Promise<{ access: string }> {
        const response = await api.post<ApiResponse<{ access: string }>>(
            API_ENDPOINTS.AUTH.REFRESH,
            { refresh: refreshToken }
        );
        return handleApiResponse(response.data);
    },
};
