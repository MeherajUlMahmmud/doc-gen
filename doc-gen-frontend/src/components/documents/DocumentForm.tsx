import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Form } from '@/components/ui/form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { DynamicFormField } from './DynamicFormField';
import type { TemplateField, SignatureGroup } from '@/types/document';
import { useAuth } from '@/context/AuthContext';

interface DocumentFormProps {
    fields: TemplateField[];
    signatureGroups: SignatureGroup[];
    onFieldChange?: (fieldName: string, value: any) => void;
    form: ReturnType<typeof useForm>;
}

export const DocumentForm: React.FC<DocumentFormProps> = ({
    fields,
    signatureGroups,
    onFieldChange,
    form,
}) => {
    const { user } = useAuth();

    // Separate regular fields from signature fields
    const regularFields = fields.filter((field) => field.type !== 'signature');
    const signatureFields = fields.filter((field) => field.type === 'signature');

    // Auto-fill fields marked as autofilled
    useEffect(() => {
        const autofilledFields = fields.filter((field) => field.is_autofilled);
        if (user && autofilledFields.length > 0) {
            autofilledFields.forEach((field) => {
                let value: any = '';
                
                // Try to match field name to user properties
                const fieldNameLower = field.name.toLowerCase();
                if (fieldNameLower.includes('name') || fieldNameLower.includes('full_name')) {
                    value = user.full_name || `${user.first_name} ${user.last_name}`.trim();
                } else if (fieldNameLower.includes('first_name') || fieldNameLower.includes('firstname')) {
                    value = user.first_name || '';
                } else if (fieldNameLower.includes('last_name') || fieldNameLower.includes('lastname')) {
                    value = user.last_name || '';
                } else if (fieldNameLower.includes('email')) {
                    value = user.email || '';
                } else if (fieldNameLower.includes('designation')) {
                    value = user.designation || '';
                } else if (fieldNameLower.includes('division')) {
                    value = user.division || '';
                }

                if (value) {
                    form.setValue(field.name, value);
                    onFieldChange?.(field.name, value);
                }
            });
        }
    }, [user, fields, form, onFieldChange]);

    return (
        <Form {...form}>
            <form className="space-y-6">
                {/* Regular Fields */}
                {regularFields.length > 0 && (
                    <div className="space-y-4">
                        {regularFields.map((field) => (
                            <DynamicFormField
                                key={field.name}
                                field={field}
                                control={form.control}
                                onChange={(value) => onFieldChange?.(field.name, value)}
                            />
                        ))}
                    </div>
                )}

                {/* Signature Groups */}
                {signatureGroups.length > 0 && (
                    <>
                        <Separator className="my-6" />
                        <div className="space-y-6">
                            <div>
                                <h3 className="text-lg font-semibold mb-4">Signatures</h3>
                                <p className="text-sm text-muted-foreground mb-4">
                                    The following signature fields will be filled during the approval process.
                                </p>
                            </div>
                            {signatureGroups.map((group, groupIndex) => (
                                <Card key={groupIndex} className="border-dashed">
                                    <CardHeader className="pb-3">
                                        <CardTitle className="text-base">{group.section_label}</CardTitle>
                                        {group.is_required && (
                                            <CardDescription>
                                                This signature group is required
                                            </CardDescription>
                                        )}
                                    </CardHeader>
                                    <CardContent className="space-y-3">
                                        {group.signature_fields.map((field) => (
                                            <DynamicFormField
                                                key={field.name}
                                                field={field}
                                                control={form.control}
                                            />
                                        ))}
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </>
                )}

                {/* Individual Signature Fields (not in groups) */}
                {signatureFields.filter(
                    (field) => !signatureGroups.some((group) =>
                        group.signature_fields.some((sf) => sf.name === field.name)
                    )
                ).length > 0 && (
                    <>
                        <Separator className="my-6" />
                        <div className="space-y-4">
                            <h3 className="text-lg font-semibold">Additional Signatures</h3>
                            {signatureFields
                                .filter(
                                    (field) => !signatureGroups.some((group) =>
                                        group.signature_fields.some((sf) => sf.name === field.name)
                                    )
                                )
                                .map((field) => (
                                    <DynamicFormField
                                        key={field.name}
                                        field={field}
                                        control={form.control}
                                    />
                                ))}
                        </div>
                    </>
                )}
            </form>
        </Form>
    );
};

