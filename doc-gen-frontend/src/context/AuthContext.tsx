import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { User, LoginRequest, RegisterRequest } from '@/types/auth';
import { authService } from '@/services/auth';
import { userService } from '@/services/users';
import { getErrorMessage } from '@/services/api';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    isAuthenticated: boolean;
    login: (data: LoginRequest) => Promise<void>;
    register: (data: RegisterRequest) => Promise<void>;
    logout: () => Promise<void>;
    refreshUser: () => Promise<void>;
    error: string | null;
    clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    // Check if user is authenticated on mount
    useEffect(() => {
        const initAuth = async () => {
            const storedUser = localStorage.getItem('user');
            const accessToken = localStorage.getItem('access_token');

            if (storedUser && accessToken) {
                try {
                    // Parse stored user
                    const parsedUser = JSON.parse(storedUser) as User;
                    setUser(parsedUser);

                    // Optionally refresh user data from server
                    await refreshUser();
                } catch (err) {
                    console.error('Failed to initialize auth:', err);
                    // Clear invalid data
                    localStorage.removeItem('user');
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                }
            }

            setLoading(false);
        };

        initAuth();
    }, []);

    const login = async (data: LoginRequest): Promise<void> => {
        try {
            setError(null);
            setLoading(true);

            const response = await authService.login(data);

            // Store tokens and user data
            localStorage.setItem('access_token', response.tokens.access);
            localStorage.setItem('refresh_token', response.tokens.refresh);
            localStorage.setItem('user', JSON.stringify(response.user));

            setUser(response.user);
        } catch (err) {
            const errorMessage = getErrorMessage(err);
            setError(errorMessage);
            throw new Error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const register = async (data: RegisterRequest): Promise<void> => {
        try {
            setError(null);
            setLoading(true);

            await authService.register(data);

            // After registration, user needs to login
            // We don't automatically log them in
        } catch (err) {
            const errorMessage = getErrorMessage(err);
            setError(errorMessage);
            throw new Error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const logout = async (): Promise<void> => {
        try {
            setError(null);
            const refreshToken = localStorage.getItem('refresh_token');

            if (refreshToken) {
                // Attempt to logout on server (blacklist token)
                try {
                    await authService.logout({ refresh_token: refreshToken });
                } catch (err) {
                    // Even if server logout fails, we still clear local data
                    console.error('Server logout failed:', err);
                }
            }

            // Clear local storage
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');

            setUser(null);
        } catch (err) {
            const errorMessage = getErrorMessage(err);
            setError(errorMessage);
            throw new Error(errorMessage);
        }
    };

    const refreshUser = async (): Promise<void> => {
        try {
            const userData = await userService.getProfile();
            setUser(userData);
            localStorage.setItem('user', JSON.stringify(userData));
        } catch (err) {
            console.error('Failed to refresh user:', err);
            // Don't throw error here, just log it
        }
    };

    const clearError = () => {
        setError(null);
    };

    const value: AuthContextType = {
        user,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
        error,
        clearError,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * Hook to use auth context
 */
export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);

    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }

    return context;
};
