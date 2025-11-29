import api, { handleApiResponse } from './api';
import type { ApiResponse } from '@/types/api';
import type {
    User,
    ProfileUpdateRequest,
    PINSetupRequest,
    TwoFactorSetupRequest,
    TwoFactorSetupResponse,
} from '@/types/auth';
import { API_ENDPOINTS } from '@/constants/urls';

/**
 * User service for user-related API calls
 */
export const userService = {
    /**
     * Get current user profile
     */
    async getProfile(): Promise<User> {
        const response = await api.get<ApiResponse<User>>(API_ENDPOINTS.USERS.PROFILE);
        return handleApiResponse(response.data);
    },

    /**
     * Update user profile (name, designation and division)
     */
    async updateProfile(data: ProfileUpdateRequest): Promise<User> {
        const response = await api.patch<ApiResponse<User>>(
            API_ENDPOINTS.USERS.PROFILE_UPDATE,
            data
        );
        return handleApiResponse(response.data);
    },

    /**
     * Upload profile picture
     */
    async uploadProfilePicture(file: File): Promise<User> {
        const formData = new FormData();
        formData.append('profile_picture', file);

        const response = await api.patch<ApiResponse<User>>(
            API_ENDPOINTS.USERS.PROFILE_UPDATE,
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
     * Upload signature file
     */
    async uploadSignature(file: File): Promise<{ signature_file: string }> {
        const formData = new FormData();
        formData.append('signature_file', file);

        const response = await api.patch<ApiResponse<{ signature_file: string }>>(
            API_ENDPOINTS.USERS.SIGNATURE_UPLOAD,
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
     * Setup or change signature PIN
     */
    async setupPIN(data: PINSetupRequest): Promise<void> {
        const response = await api.post<ApiResponse<void>>(
            API_ENDPOINTS.USERS.PIN_SETUP,
            data
        );
        return handleApiResponse(response.data);
    },

    /**
     * Get 2FA QR code
     */
    async get2FAQRCode(): Promise<TwoFactorSetupResponse> {
        const response = await api.get<ApiResponse<TwoFactorSetupResponse>>(
            API_ENDPOINTS.USERS.TWO_FA_SETUP
        );
        return handleApiResponse(response.data);
    },

    /**
     * Enable or disable 2FA
     */
    async toggle2FA(data: TwoFactorSetupRequest): Promise<TwoFactorSetupResponse> {
        const response = await api.post<ApiResponse<TwoFactorSetupResponse>>(
            API_ENDPOINTS.USERS.TWO_FA_SETUP,
            data
        );
        return handleApiResponse(response.data);
    },
};
