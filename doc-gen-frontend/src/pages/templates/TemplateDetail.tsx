import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { ArrowLeft, FileText, Calendar, Clock, CheckCircle2, XCircle, Download, Plus, History } from 'lucide-react';
import { documentService } from '@/services/documents';
import type { Template } from '@/types/document';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { ROUTES } from '@/constants/urls';

export const TemplateDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [template, setTemplate] = useState<Template | null>(null);
    const [versions, setVersions] = useState<Template[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadingVersions, setLoadingVersions] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (id) {
            loadTemplate(id);
        }
    }, [id]);

    const loadTemplate = async (templateId: string) => {
        try {
            setLoading(true);
            setError(null);
            const data = await documentService.getTemplate(templateId);
            setTemplate(data);
            // Load versions after template is loaded
            loadVersions(templateId);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to load template';
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const loadVersions = async (templateId: string) => {
        try {
            setLoadingVersions(true);
            const versionsData = await documentService.getTemplateVersions(templateId);
            setVersions(versionsData);
        } catch (err) {
            // Don't show error toast for versions, just log it
            console.error('Failed to load template versions:', err);
        } finally {
            setLoadingVersions(false);
        }
    };

    const handleCreateDocument = () => {
        if (template) {
            navigate(`${ROUTES.DOCUMENTS_NEW}?template=${template.id}`);
        }
    };

    const handleBack = () => {
        navigate(ROUTES.TEMPLATES);
    };

    if (loading) {
        return (
            <AppLayout>
                <div className="flex justify-center items-center h-64">
                    <LoadingSpinner size="lg" text="Loading template details..." />
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
                    <div className="flex items-center gap-2">
                        <Button onClick={handleCreateDocument}>
                            <Plus className="mr-2 h-4 w-4" />
                            Create Document
                        </Button>
                        <Button variant="outline">
                            <Download className="mr-2 h-4 w-4" />
                            Download Template File
                        </Button>
                    </div>
                </div>

                {/* Template Details Card */}
                <Card>
                    <CardHeader>
                        <div className="flex items-start justify-between">
                            <div className="space-y-2">
                                <div className="flex items-center gap-3">
                                    <FileText className="h-8 w-8 text-primary" />
                                    <CardTitle className="text-3xl">{template.title}</CardTitle>
                                </div>
                                {template.description && (
                                    <CardDescription className="text-base">
                                        {template.description}
                                    </CardDescription>
                                )}
                            </div>
                            <Badge variant={template.is_active ? 'default' : 'secondary'} className="text-sm">
                                {template.is_active ? (
                                    <>
                                        <CheckCircle2 className="mr-1 h-3 w-3" />
                                        Active
                                    </>
                                ) : (
                                    <>
                                        <XCircle className="mr-1 h-3 w-3" />
                                        Inactive
                                    </>
                                )}
                            </Badge>
                        </div>
                    </CardHeader>

                    <CardContent className="space-y-6">
                        {/* Template Information */}
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                                    <FileText className="h-5 w-5 text-primary" />
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Version</p>
                                    <p className="text-lg font-semibold">v{template.version}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                                <div className="h-10 w-10 rounded-full bg-blue-500/10 flex items-center justify-center">
                                    <Calendar className="h-5 w-5 text-blue-500" />
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Created</p>
                                    <p className="text-lg font-semibold">
                                        {format(new Date(template.created_at), 'MMM d, yyyy')}
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                                <div className="h-10 w-10 rounded-full bg-green-500/10 flex items-center justify-center">
                                    <Clock className="h-5 w-5 text-green-500" />
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Last Updated</p>
                                    <p className="text-lg font-semibold">
                                        {format(new Date(template.updated_at), 'MMM d, yyyy')}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Template Versions */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <History className="h-5 w-5 text-primary" />
                            <CardTitle>Template Versions</CardTitle>
                        </div>
                        <CardDescription>
                            All versions of this template
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {loadingVersions ? (
                            <div className="flex justify-center py-8">
                                <LoadingSpinner size="md" text="Loading versions..." />
                            </div>
                        ) : versions.length > 0 ? (
                            <div className="space-y-3">
                                {versions.map((version) => (
                                    <div
                                        key={version.id}
                                        className={`flex items-center justify-between p-4 rounded-lg border ${version.id === template?.id
                                            ? 'bg-primary/5 border-primary'
                                            : 'bg-muted border-border'
                                            }`}
                                    >
                                        <div className="flex items-center gap-4 flex-1">
                                            <div className="flex items-center gap-3">
                                                <div className={`h-10 w-10 rounded-full flex items-center justify-center ${version.id === template?.id
                                                    ? 'bg-primary/10'
                                                    : 'bg-muted-foreground/10'
                                                    }`}>
                                                    <FileText className={`h-5 w-5 ${version.id === template?.id
                                                        ? 'text-primary'
                                                        : 'text-muted-foreground'
                                                        }`} />
                                                </div>
                                                <div>
                                                    <div className="flex items-center gap-2">
                                                        <p className="font-semibold">Version {version.version}</p>
                                                        {version.id === template?.id && (
                                                            <Badge variant="default" className="text-xs">
                                                                Current
                                                            </Badge>
                                                        )}
                                                        {!version.is_active && (
                                                            <Badge variant="secondary" className="text-xs">
                                                                Inactive
                                                            </Badge>
                                                        )}
                                                    </div>
                                                    <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                                                        <span className="flex items-center gap-1">
                                                            <Calendar className="h-3 w-3" />
                                                            Created: {format(new Date(version.created_at), 'MMM d, yyyy')}
                                                        </span>
                                                        <span className="flex items-center gap-1">
                                                            <Clock className="h-3 w-3" />
                                                            Last Updated: {format(new Date(version.updated_at), 'MMM d, yyyy')}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        {version.id !== template?.id && (
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => {
                                                    navigate(ROUTES.TEMPLATE_DETAIL(version.id));
                                                }}
                                            >
                                                View
                                            </Button>
                                        )}
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-muted-foreground text-center py-8">
                                No versions found
                            </p>
                        )}
                    </CardContent>
                </Card>

                {/* Additional Information */}
                <Card>
                    <CardHeader>
                        <CardTitle>About This Template</CardTitle>
                        <CardDescription>
                            Use this template to generate documents with custom fields
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="prose prose-sm max-w-none">
                            {template.description ? (
                                <p className="text-muted-foreground">{template.description}</p>
                            ) : (
                                <p className="text-muted-foreground italic">No additional description available</p>
                            )}
                        </div>

                        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800">
                            <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">How to Use</h4>
                            <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800 dark:text-blue-200">
                                <li>Click "Create Document from Template" button above</li>
                                <li>Fill in the required fields in the document form</li>
                                <li>Preview your document before generating</li>
                                <li>Download or save your generated document</li>
                            </ol>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </AppLayout>
    );
};
