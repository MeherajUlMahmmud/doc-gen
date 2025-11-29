import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { FileText, FileSignature, CheckCircle2, XCircle } from 'lucide-react';
import type { Template, TemplateField, SignatureGroup } from '@/types/document';

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

    return (
        <div className="space-y-6 h-full overflow-y-auto">
            {/* Template Info */}
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-3">
                        <FileText className="h-6 w-6 text-primary" />
                        <div className="flex-1">
                            <CardTitle className="text-xl">{template.title}</CardTitle>
                            {template.description && (
                                <CardDescription className="mt-1">{template.description}</CardDescription>
                            )}
                        </div>
                    </div>
                </CardHeader>
            </Card>

            {/* Field Values Summary */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">Field Values</CardTitle>
                    <CardDescription>
                        Preview of all field values that will be used in the document
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {regularFields.length > 0 ? (
                        <div className="space-y-3">
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
                </CardContent>
            </Card>

            {/* Signature Fields Preview */}
            {(signatureGroups.length > 0 || signatureFields.length > 0) && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <FileSignature className="h-5 w-5" />
                            Signature Fields
                        </CardTitle>
                        <CardDescription>
                            These fields will be filled with signatures during the approval process
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {signatureGroups.length > 0 && (
                            <div className="space-y-4">
                                {signatureGroups.map((group, groupIndex) => (
                                    <div key={groupIndex} className="space-y-2">
                                        <div className="flex items-center gap-2">
                                            <h4 className="font-semibold text-sm">{group.section_label}</h4>
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
                                    <h4 className="font-semibold text-sm">Additional Signatures</h4>
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
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

