import React, { useState, useMemo } from 'react';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, FileSignature, CheckCircle2, XCircle, Eye, List, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { Template, TemplateField, SignatureGroup } from '@/types/document';
import { documentService } from '@/services/documents';

interface DocumentPreviewPaneProps {
    template: Template;
    formValues: Record<string, any>;
    fields: TemplateField[];
    signatureGroups: SignatureGroup[];
}

export const DocumentPreviewPane: React.FC<DocumentPreviewPaneProps> = ({
    template,
    formValues,
    fields,
    signatureGroups,
}) => {
    const [activeTab, setActiveTab] = useState<'visual' | 'fields'>('visual');
    const [serverPreview, setServerPreview] = useState<string | null>(null);
    const [loadingServerPreview, setLoadingServerPreview] = useState(false);

    const getFieldValue = (fieldName: string): string => {
        const value = formValues[fieldName];
        if (value === undefined || value === null || value === '') {
            return '[Not filled]';
        }
        if (typeof value === 'boolean') {
            return value ? 'Yes' : 'No';
        }
        return String(value);
    };

    const regularFields = fields.filter((field) => field.type !== 'signature');
    const signatureFields = fields.filter((field) => field.type === 'signature');

    // Client-side instant preview - Simple template string replacement
    const clientPreview = useMemo(() => {
        // Create a simple document structure with filled values
        const sections: string[] = [];

        // Add title
        sections.push(`<div class="document-header" style="text-align: center; margin-bottom: 2em; padding-bottom: 1em; border-bottom: 2px solid #e5e7eb;">
            <h1 style="font-size: 1.875rem; font-weight: bold; margin-bottom: 0.5em;">${template.title}</h1>
            ${template.description ? `<p style="color: #6b7280; font-size: 0.875rem;">${template.description}</p>` : ''}
        </div>`);

        // Group fields by sections if they have prefixes (e.g., "company_", "user_")
        const fieldsBySection = new Map<string, TemplateField[]>();
        const ungroupedFields: TemplateField[] = [];

        regularFields.forEach(field => {
            const parts = field.name.split('_');
            if (parts.length > 1) {
                const section = parts[0];
                if (!fieldsBySection.has(section)) {
                    fieldsBySection.set(section, []);
                }
                fieldsBySection.get(section)!.push(field);
            } else {
                ungroupedFields.push(field);
            }
        });

        // Render grouped fields
        fieldsBySection.forEach((sectionFields, sectionName) => {
            sections.push(`<div class="section" style="margin-bottom: 1.5em;">
                <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 0.75em; text-transform: capitalize; color: #374151;">
                    ${sectionName.replace(/_/g, ' ')}
                </h3>
                <div style="display: grid; gap: 0.75rem;">
                    ${sectionFields.map(field => {
                        const value = getFieldValue(field.name);
                        const isFilled = value !== '[Not filled]';
                        return `<div style="display: flex; justify-content: space-between; padding: 0.75rem; border: 1px solid #e5e7eb; border-radius: 0.375rem; background: ${isFilled ? '#ffffff' : '#f9fafb'};">
                            <span style="font-weight: 500; color: #374151;">${field.label}:</span>
                            <span style="color: ${isFilled ? '#111827' : '#9ca3af'}; ${isFilled ? '' : 'font-style: italic;'}">${value}</span>
                        </div>`;
                    }).join('')}
                </div>
            </div>`);
        });

        // Render ungrouped fields
        if (ungroupedFields.length > 0) {
            sections.push(`<div class="section" style="margin-bottom: 1.5em;">
                <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 0.75em; color: #374151;">
                    Document Details
                </h3>
                <div style="display: grid; gap: 0.75rem;">
                    ${ungroupedFields.map(field => {
                        const value = getFieldValue(field.name);
                        const isFilled = value !== '[Not filled]';
                        return `<div style="display: flex; justify-content: space-between; padding: 0.75rem; border: 1px solid #e5e7eb; border-radius: 0.375rem; background: ${isFilled ? '#ffffff' : '#f9fafb'};">
                            <span style="font-weight: 500; color: #374151;">${field.label}:</span>
                            <span style="color: ${isFilled ? '#111827' : '#9ca3af'}; ${isFilled ? '' : 'font-style: italic;'}">${value}</span>
                        </div>`;
                    }).join('')}
                </div>
            </div>`);
        }

        // Add signature placeholders
        if (signatureGroups.length > 0) {
            sections.push(`<div class="signatures" style="margin-top: 2em; padding-top: 1.5em; border-top: 2px solid #e5e7eb;">
                <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1em; color: #374151;">
                    Signature Fields
                </h3>
                ${signatureGroups.map(group => `
                    <div style="margin-bottom: 1.5em; padding: 1rem; border: 1px dashed #d1d5db; border-radius: 0.375rem; background: #f9fafb;">
                        <h4 style="font-weight: 600; margin-bottom: 0.5em; color: #374151;">${group.section_label}</h4>
                        <div style="display: grid; gap: 0.5rem;">
                            ${group.signature_fields.map(field => `
                                <div style="display: flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.875rem;">
                                    <span>📝</span>
                                    <span>${field.label}</span>
                                    <span style="margin-left: auto; font-style: italic;">Pending signature</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>`);
        }

        return `<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 2rem; background: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            ${sections.join('')}
        </div>`;
    }, [template, formValues, regularFields, signatureGroups]);

    // Server-side accurate preview on demand
    const handleServerPreview = async () => {
        try {
            setLoadingServerPreview(true);

            const fieldsData: Record<string, any> = {};
            regularFields.forEach((field) => {
                const value = formValues[field.name];
                if (value !== undefined && value !== null && value !== '') {
                    fieldsData[field.name] = value;
                }
            });

            const result = await documentService.previewTemplate(template.id, fieldsData);
            setServerPreview(result.html);
            setActiveTab('visual');
        } catch (err) {
            console.error('Error generating server preview:', err);
        } finally {
            setLoadingServerPreview(false);
        }
    };

    return (
        <div className="h-full flex flex-col">
            <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'visual' | 'fields')} className="h-full flex flex-col">
                <div className="space-y-3">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="visual" className="gap-2">
                            <Eye className="h-4 w-4" />
                            Live Preview
                        </TabsTrigger>
                        <TabsTrigger value="fields" className="gap-2">
                            <List className="h-4 w-4" />
                            Field Summary
                        </TabsTrigger>
                    </TabsList>

                    {/* Option to generate accurate preview */}
                    {activeTab === 'visual' && (
                        <div className="flex items-center justify-between p-2 bg-blue-50 dark:bg-blue-950 rounded-md border border-blue-200 dark:border-blue-800">
                            <p className="text-xs text-blue-800 dark:text-blue-200">
                                {serverPreview ? 'Showing server-generated preview' : 'Showing instant preview'}
                            </p>
                            <Button
                                size="sm"
                                variant="outline"
                                onClick={handleServerPreview}
                                disabled={loadingServerPreview}
                                className="h-7 text-xs"
                            >
                                {loadingServerPreview ? (
                                    <>
                                        <RefreshCw className="mr-1 h-3 w-3 animate-spin" />
                                        Generating...
                                    </>
                                ) : (
                                    <>
                                        <RefreshCw className="mr-1 h-3 w-3" />
                                        Generate Accurate Preview
                                    </>
                                )}
                            </Button>
                        </div>
                    )}
                </div>

                {/* Visual Preview Tab */}
                <TabsContent value="visual" className="flex-1 overflow-y-auto mt-4">
                    <div className="space-y-4">
                        {/* Template Info */}
                        <div className="flex items-center gap-3 pb-3 border-b">
                            <FileText className="h-5 w-5 text-primary" />
                            <div className="flex-1">
                                <h3 className="font-semibold">{template.title}</h3>
                                {template.description && (
                                    <p className="text-sm text-muted-foreground">{template.description}</p>
                                )}
                            </div>
                        </div>

                        {/* Preview */}
                        <div className="bg-white dark:bg-slate-950 rounded-lg border shadow-sm">
                            <div
                                className="prose prose-sm max-w-none dark:prose-invert"
                                dangerouslySetInnerHTML={{ __html: serverPreview || clientPreview }}
                            />
                        </div>
                    </div>
                </TabsContent>

                {/* Field Summary Tab */}
                <TabsContent value="fields" className="flex-1 overflow-y-auto mt-4">
                    <div className="space-y-4">
                        {/* Field Values Summary */}
                        <div className="space-y-3">
                            <h4 className="font-semibold text-sm">Field Values</h4>
                            {regularFields.length > 0 ? (
                                <div className="space-y-2">
                                    {regularFields.map((field) => {
                                        const value = getFieldValue(field.name);
                                        const isFilled = value !== '[Not filled]';

                                        return (
                                            <div
                                                key={field.name}
                                                className="flex items-start justify-between gap-4 p-3 rounded-md border bg-card"
                                            >
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="font-medium text-sm">{field.label}</span>
                                                        {field.required && (
                                                            <Badge variant="outline" className="text-xs">
                                                                Required
                                                            </Badge>
                                                        )}
                                                        {isFilled ? (
                                                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                                                        ) : (
                                                            <XCircle className="h-4 w-4 text-muted-foreground" />
                                                        )}
                                                    </div>
                                                    <p
                                                        className={`text-sm ${
                                                            isFilled
                                                                ? 'text-foreground'
                                                                : 'text-muted-foreground italic'
                                                        }`}
                                                    >
                                                        {value}
                                                    </p>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <p className="text-sm text-muted-foreground text-center py-4">
                                    No regular fields in this template
                                </p>
                            )}
                        </div>

                        {/* Signature Fields Preview */}
                        {(signatureGroups.length > 0 || signatureFields.length > 0) && (
                            <>
                                <Separator />
                                <div className="space-y-3">
                                    <h4 className="font-semibold text-sm flex items-center gap-2">
                                        <FileSignature className="h-4 w-4" />
                                        Signature Fields
                                    </h4>
                                    <p className="text-sm text-muted-foreground">
                                        These fields will be filled with signatures during the approval process
                                    </p>
                                    {signatureGroups.length > 0 && (
                                        <div className="space-y-3">
                                            {signatureGroups.map((group, groupIndex) => (
                                                <div key={groupIndex} className="space-y-2">
                                                    <div className="flex items-center gap-2">
                                                        <h5 className="font-medium text-sm">{group.section_label}</h5>
                                                        {group.is_required && (
                                                            <Badge variant="outline" className="text-xs">
                                                                Required
                                                            </Badge>
                                                        )}
                                                    </div>
                                                    <div className="pl-4 space-y-2 border-l-2 border-dashed">
                                                        {group.signature_fields.map((field) => (
                                                            <div
                                                                key={field.name}
                                                                className="flex items-center gap-2 text-sm text-muted-foreground"
                                                            >
                                                                <FileSignature className="h-4 w-4" />
                                                                <span>{field.label}</span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {signatureFields.filter(
                                        (field) => !signatureGroups.some((group) =>
                                            group.signature_fields.some((sf) => sf.name === field.name)
                                        )
                                    ).length > 0 && (
                                        <>
                                            {signatureGroups.length > 0 && <Separator />}
                                            <div className="space-y-2">
                                                <h5 className="font-medium text-sm">Additional Signatures</h5>
                                                {signatureFields
                                                    .filter(
                                                        (field) => !signatureGroups.some((group) =>
                                                            group.signature_fields.some((sf) => sf.name === field.name)
                                                        )
                                                    )
                                                    .map((field) => (
                                                        <div
                                                            key={field.name}
                                                            className="flex items-center gap-2 text-sm text-muted-foreground pl-4"
                                                        >
                                                            <FileSignature className="h-4 w-4" />
                                                            <span>{field.label}</span>
                                                        </div>
                                                    ))}
                                            </div>
                                        </>
                                    )}
                                </div>
                            </>
                        )}
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
};
