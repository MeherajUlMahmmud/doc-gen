/**
 * User model from backend
 */
export interface User {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    full_name: string;
    profile_picture?: string;
    signature_file?: string;
    is_verified: boolean;
    is_staff: boolean;
    is_admin: boolean;
    designation?: string;
    division?: string;
    two_factor_enabled: boolean;
    created_at: string;
    updated_at: string;
    last_login?: string;
}

/**
 * Login request payload
 */
export interface LoginRequest {
    email: string;
    password: string;
}

/**
 * Login response data
 */
export interface LoginResponse {
    user: User;
    tokens: {
        access: string;
        refresh: string;
    };
}

/**
 * Register request payload
 */
export interface RegisterRequest {
    email: string;
    first_name: string;
    last_name: string;
    password: string;
    password_confirm: string;
}

/**
 * Register response data
 */
export interface RegisterResponse {
    user: User;
}

/**
 * Logout request payload
 */
export interface LogoutRequest {
    refresh_token: string;
}

/**
 * Profile update request payload
 */
export interface ProfileUpdateRequest {
    first_name?: string;
    last_name?: string;
    designation?: string;
    division?: string;
}

/**
 * PIN setup request payload
 */
export interface PINSetupRequest {
    pin: string;
}

/**
 * 2FA setup request payload
 */
export interface TwoFactorSetupRequest {
    action: 'enable' | 'disable';
}

/**
 * 2FA setup response data
 */
export interface TwoFactorSetupResponse {
    qr_code?: string;
    secret?: string;
    two_factor_enabled?: boolean;
}
