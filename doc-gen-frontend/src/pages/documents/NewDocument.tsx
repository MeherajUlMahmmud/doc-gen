import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { ArrowLeft, FileText } from 'lucide-react';
import { documentService } from '@/services/documents';
import type { Template } from '@/types/document';
import { toast } from 'sonner';
import { ROUTES } from '@/constants/urls';

export const NewDocumentPage: React.FC = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const templateId = searchParams.get('template');

    const [template, setTemplate] = useState<Template | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (templateId) {
            loadTemplate(templateId);
        } else {
            setError('No template selected');
            setLoading(false);
        }
    }, [templateId]);

    const loadTemplate = async (id: string) => {
        try {
            setLoading(true);
            setError(null);
            const data = await documentService.getTemplate(id);
            setTemplate(data);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to load template';
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const handleBack = () => {
        navigate(ROUTES.TEMPLATES);
    };

    if (loading) {
        return (
            <AppLayout>
                <div className="flex justify-center items-center h-64">
                    <LoadingSpinner size="lg" text="Loading template..." />
                </div>
            </AppLayout>
        );
    }

    if (error || !template) {
        return (
            <AppLayout>
                <div className="space-y-4">
                    <Button variant="ghost" onClick={handleBack}>
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Back to Templates
                    </Button>
                    <ErrorAlert message={error || 'Template not found'} />
                </div>
            </AppLayout>
        );
    }

    return (
        <AppLayout>
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <Button variant="ghost" onClick={handleBack}>
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Back to Templates
                    </Button>
                </div>

                {/* Document Form */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center gap-3">
                            <FileText className="h-8 w-8 text-primary" />
                            <div>
                                <CardTitle className="text-2xl">Create New Document</CardTitle>
                                <CardDescription className="mt-1">
                                    Using template: <span className="font-semibold">{template.title}</span>
                                </CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="text-center py-16">
                            <FileText className="h-16 w-16 mx-auto text-muted-foreground opacity-50 mb-4" />
                            <h3 className="text-lg font-semibold mb-2">Document Form Coming Soon</h3>
                            <p className="text-muted-foreground mb-6">
                                This feature is under development. You'll be able to fill in template fields and generate documents here.
                            </p>
                            <div className="space-y-2 text-sm text-muted-foreground">
                                <p>Planned features:</p>
                                <ul className="list-disc list-inside space-y-1">
                                    <li>Dynamic form fields based on template</li>
                                    <li>Real-time document preview</li>
                                    <li>Save as draft functionality</li>
                                    <li>Export to multiple formats (PDF, DOCX)</li>
                                    <li>Signature workflow support</li>
                                </ul>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </AppLayout>
    );
};
