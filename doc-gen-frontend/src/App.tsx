import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { AuthProvider } from '@/context/AuthContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Toaster } from '@/components/ui/sonner';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ROUTES } from '@/constants/urls';

// Lazy load pages
const LoginPage = lazy(() => import('@/pages/auth/Login').then(module => ({ default: module.LoginPage })));
const RegisterPage = lazy(() => import('@/pages/auth/Register').then(module => ({ default: module.RegisterPage })));
const Dashboard = lazy(() => import('@/pages/Dashboard').then(module => ({ default: module.Dashboard })));
const ProfilePage = lazy(() => import('@/pages/profile/Profile').then(module => ({ default: module.ProfilePage })));
const TemplateListPage = lazy(() => import('@/pages/templates/TemplateList').then(module => ({ default: module.TemplateListPage })));
const TemplateDetailPage = lazy(() => import('@/pages/templates/TemplateDetail').then(module => ({ default: module.TemplateDetailPage })));
const DocumentListPage = lazy(() => import('@/pages/documents/DocumentList').then(module => ({ default: module.DocumentListPage })));
const NewDocumentPage = lazy(() => import('@/pages/documents/NewDocument').then(module => ({ default: module.NewDocumentPage })));
const PendingSignaturesPage = lazy(() => import('@/pages/documents/PendingSignatures').then(module => ({ default: module.PendingSignaturesPage })));

// Loading fallback component
const PageLoader = () => (
    <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="Loading..." />
    </div>
);

function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Suspense fallback={<PageLoader />}>
                    <Routes>
                        {/* Public Routes */}
                        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
                        <Route path={ROUTES.REGISTER} element={<RegisterPage />} />

                    {/* Protected Routes */}
                    <Route
                        path={ROUTES.HOME}
                        element={
                            <ProtectedRoute>
                                <Dashboard />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path={ROUTES.PROFILE}
                        element={
                            <ProtectedRoute>
                                <ProfilePage />
                            </ProtectedRoute>
                        }
                    />

                    {/* Document & Template Routes */}
                    <Route
                        path={ROUTES.TEMPLATES}
                        element={
                            <ProtectedRoute>
                                <TemplateListPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path={ROUTES.DOCUMENTS}
                        element={
                            <ProtectedRoute>
                                <DocumentListPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path={ROUTES.DOCUMENTS_PENDING_SIGNATURES}
                        element={
                            <ProtectedRoute>
                                <PendingSignaturesPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path={ROUTES.DOCUMENTS_NEW}
                        element={
                            <ProtectedRoute>
                                <NewDocumentPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/documents/:id/edit"
                        element={
                            <ProtectedRoute>
                                <div>Edit Document Page (Coming Soon)</div>
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/templates/:id"
                        element={
                            <ProtectedRoute>
                                <TemplateDetailPage />
                            </ProtectedRoute>
                        }
                    />

                        {/* Catch all - redirect to home */}
                        <Route path="*" element={<Navigate to={ROUTES.HOME} replace />} />
                    </Routes>
                </Suspense>

                {/* Toast notifications */}
                <Toaster position="top-right" richColors />
            </AuthProvider>
        </BrowserRouter>
    );
}

export default App;
