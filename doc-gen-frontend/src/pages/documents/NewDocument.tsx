import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { AppLayout } from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { DocumentForm } from '@/components/documents/DocumentForm';
import { DocumentPreviewPane } from '@/components/documents/DocumentPreviewPane';
import { ArrowLeft, FileText, Save, FileCheck, Loader2 } from 'lucide-react';
import { documentService } from '@/services/documents';
import type { Template } from '@/types/document';
import { toast } from 'sonner';
import { ROUTES } from '@/constants/urls';
import { createDocumentSchema } from '@/schemas/document.schema';

export const NewDocumentPage: React.FC = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const templateId = searchParams.get('template');

    const [template, setTemplate] = useState<Template | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [saving, setSaving] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [documentTitle, setDocumentTitle] = useState('');

    // Initialize form with dynamic schema
    const fields = template?.fields || [];
    const signatureGroups = template?.signature_groups || [];
    const schema = createDocumentSchema(fields);
    const form = useForm({
        resolver: zodResolver(schema),
        defaultValues: {
            title: '',
            ...fields.reduce((acc, field) => {
                acc[field.name] = field.type === 'checkbox' ? false : field.type === 'number' ? undefined : '';
                return acc;
            }, {} as Record<string, any>),
        },
    });

    const [formValues, setFormValues] = useState<Record<string, any>>({});

    useEffect(() => {
        if (templateId) {
            loadTemplate(templateId);
        } else {
            setError('No template selected');
            setLoading(false);
        }
    }, [templateId]);

    // Watch form values for preview
    useEffect(() => {
        const subscription = form.watch((values) => {
            setFormValues(values as Record<string, any>);
        });
        return () => subscription.unsubscribe();
    }, [form]);

    const loadTemplate = async (id: string) => {
        try {
            setLoading(true);
            setError(null);
            const data = await documentService.getTemplate(id);
            setTemplate(data);
            
            // Reset form with new schema
            const newFields = data.fields || [];
            form.reset({
                title: '',
                ...newFields.reduce((acc, field) => {
                    acc[field.name] = field.type === 'checkbox' ? false : field.type === 'number' ? undefined : '';
                    return acc;
                }, {} as Record<string, any>),
            });
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

    const handleFieldChange = (fieldName: string, value: any) => {
        setFormValues((prev) => ({ ...prev, [fieldName]: value }));
    };

    const handleSaveDraft = async () => {
        if (!template) return;

        try {
            setSaving(true);
            const formData = form.getValues();
            const fieldsData = { ...formData };
            delete fieldsData.title;

            await documentService.saveDraft(template.id, fieldsData);
            toast.success('Draft saved successfully');
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to save draft';
            toast.error(errorMessage);
        } finally {
            setSaving(false);
        }
    };

    const handleGenerate = async () => {
        if (!template) return;

        try {
            const isValid = await form.trigger();
            if (!isValid) {
                toast.error('Please fill in all required fields');
                return;
            }

            setGenerating(true);
            const formData = form.getValues();
            const title = documentTitle || (typeof formData.title === 'string' ? formData.title : '') || `Document from ${template.title}`;
            const fieldsData: Record<string, any> = { ...formData };
            delete fieldsData.title;

            await documentService.createDocument({
                template_id: template.id,
                title: title,
                fields: fieldsData,
            });

            toast.success('Document generated successfully');
            navigate(ROUTES.DOCUMENTS);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to generate document';
            toast.error(errorMessage);
        } finally {
            setGenerating(false);
        }
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

    if (!template || !template.fields) {
        return (
            <AppLayout>
                <div className="space-y-4">
                    <Button variant="ghost" onClick={handleBack}>
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Back to Templates
                    </Button>
                    <ErrorAlert message="Template fields could not be loaded. Please try again." />
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

                {/* Document Title */}
                <Card>
                    <CardHeader>
                        <CardTitle>Document Title</CardTitle>
                        <CardDescription>
                            Enter a name for this document
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            <Label htmlFor="document-title">Title</Label>
                            <Input
                                id="document-title"
                                placeholder="Enter document title"
                                value={documentTitle}
                                onChange={(e) => setDocumentTitle(e.target.value)}
                                maxLength={255}
                            />
                        </div>
                    </CardContent>
                </Card>

                {/* Split Layout: Form and Preview */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Left Side: Form */}
                    <div className="space-y-6">
                        <Card>
                            <CardHeader>
                                <div className="flex items-center gap-3">
                                    <FileText className="h-6 w-6 text-primary" />
                                    <div>
                                        <CardTitle>Fill Document Fields</CardTitle>
                                        <CardDescription>
                                            Template: {template.title}
                                        </CardDescription>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <DocumentForm
                                    fields={fields}
                                    signatureGroups={signatureGroups}
                                    form={form}
                                    onFieldChange={handleFieldChange}
                                />
                            </CardContent>
                        </Card>

                        {/* Action Buttons */}
                        <Card>
                            <CardContent className="pt-6">
                                <div className="flex flex-col sm:flex-row gap-3">
                                    <Button
                                        variant="outline"
                                        onClick={handleSaveDraft}
                                        disabled={saving || generating}
                                        className="flex-1"
                                    >
                                        {saving ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                Saving...
                                            </>
                                        ) : (
                                            <>
                                                <Save className="mr-2 h-4 w-4" />
                                                Save Draft
                                            </>
                                        )}
                                    </Button>
                                    <Button
                                        onClick={handleGenerate}
                                        disabled={saving || generating}
                                        className="flex-1"
                                    >
                                        {generating ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                Generating...
                                            </>
                                        ) : (
                                            <>
                                                <FileCheck className="mr-2 h-4 w-4" />
                                                Generate Document
                                            </>
                                        )}
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Right Side: Preview */}
                    <div className="lg:sticky lg:top-6 lg:h-[calc(100vh-8rem)]">
                        <Card className="h-full">
                            <CardHeader>
                                <CardTitle>Preview</CardTitle>
                                <CardDescription>
                                    Real-time preview of your document
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <DocumentPreviewPane
                                    template={template}
                                    formValues={formValues}
                                    fields={fields}
                                    signatureGroups={signatureGroups}
                                />
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
};
