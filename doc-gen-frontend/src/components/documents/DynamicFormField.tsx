import React from 'react';
import { Control } from 'react-hook-form';
import { FormField, FormItem, FormLabel, FormControl, FormMessage, FormDescription } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { FileSignature } from 'lucide-react';
import { UserPicker } from './UserPicker';
import type { TemplateField } from '@/types/document';

interface DynamicFormFieldProps {
    field: TemplateField;
    control: Control<any>;
    onChange?: (value: any) => void;
    enableSignatorySelection?: boolean;
}

export const DynamicFormField: React.FC<DynamicFormFieldProps> = ({
    field,
    control,
    onChange,
    enableSignatorySelection = false,
}) => {
    const isRequired = field.required || field.validation.toLowerCase().includes('required');

    // Handle signature fields with signatory selection
    if (field.type === 'signature') {
        if (enableSignatorySelection) {
            return (
                <FormField
                    control={control}
                    name={field.name}
                    render={({ field: formField }) => (
                        <FormItem>
                            <FormLabel className="flex items-center gap-2">
                                {field.label}
                                {isRequired && <span className="text-destructive">*</span>}
                            </FormLabel>
                            <FormControl>
                                <UserPicker
                                    value={formField.value || []}
                                    onChange={(userIds) => {
                                        formField.onChange(userIds);
                                        onChange?.(userIds);
                                    }}
                                    multiple={false}
                                    placeholder="Select signatory..."
                                />
                            </FormControl>
                            <FormDescription>
                                Select a user to sign this field.
                            </FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />
            );
        }

        // Read-only signature field (for document viewing)
        return (
            <FormField
                control={control}
                name={field.name}
                render={() => (
                    <FormItem>
                        <FormLabel className="flex items-center gap-2">
                            {field.label}
                            {isRequired && <span className="text-destructive">*</span>}
                        </FormLabel>
                        <FormControl>
                            <div className="flex items-center gap-2 p-4 border rounded-md bg-muted/50">
                                <FileSignature className="h-5 w-5 text-muted-foreground" />
                                <span className="text-sm text-muted-foreground">
                                    Signature will be applied during document approval
                                </span>
                            </div>
                        </FormControl>
                        <FormDescription>
                            This field will be filled with your signature when you approve the document.
                        </FormDescription>
                        <FormMessage />
                    </FormItem>
                )}
            />
        );
    }

    // Handle checkbox fields
    if (field.type === 'checkbox') {
        return (
            <FormField
                control={control}
                name={field.name}
                rules={isRequired ? { required: `${field.label} is required` } : {}}
                render={({ field: formField }) => (
                    <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                        <FormControl>
                            <Checkbox
                                checked={formField.value || false}
                                onCheckedChange={(checked) => {
                                    formField.onChange(checked);
                                    onChange?.(checked);
                                }}
                            />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                            <FormLabel className="flex items-center gap-2">
                                {field.label}
                                {isRequired && <span className="text-destructive">*</span>}
                            </FormLabel>
                            <FormDescription>
                                Check to indicate {field.label.toLowerCase()}
                            </FormDescription>
                        </div>
                        <FormMessage />
                    </FormItem>
                )}
            />
        );
    }

    // Handle select/dropdown fields (text fields with options)
    if (field.options && field.options.length > 0) {
        return (
            <FormField
                control={control}
                name={field.name}
                rules={isRequired ? {
                    required: `${field.label} is required`,
                } : {}}
                render={({ field: formField }) => (
                    <FormItem>
                        <FormLabel className="flex items-center gap-2">
                            {field.label}
                            {isRequired && <span className="text-destructive">*</span>}
                        </FormLabel>
                        <Select
                            onValueChange={(val) => {
                                formField.onChange(val);
                                onChange?.(val);
                            }}
                            value={formField.value || ''}
                        >
                            <FormControl>
                                <SelectTrigger>
                                    <SelectValue placeholder={`Select ${field.label.toLowerCase()}`} />
                                </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                                {field.options.map((option) => (
                                    <SelectItem key={option} value={option}>
                                        {option}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <FormDescription>
                            Choose from the available options
                        </FormDescription>
                        <FormMessage />
                    </FormItem>
                )}
            />
        );
    }

    // Handle number fields
    if (field.type === 'number') {
        return (
            <FormField
                control={control}
                name={field.name}
                rules={{
                    ...(isRequired ? { required: `${field.label} is required` } : {}),
                    ...(field.min_value !== null ? {
                        min: {
                            value: field.min_value,
                            message: `Minimum value is ${field.min_value}`,
                        },
                    } : {}),
                    ...(field.max_value !== null ? {
                        max: {
                            value: field.max_value,
                            message: `Maximum value is ${field.max_value}`,
                        },
                    } : {}),
                }}
                render={({ field: formField }) => (
                    <FormItem>
                        <FormLabel className="flex items-center gap-2">
                            {field.label}
                            {isRequired && <span className="text-destructive">*</span>}
                        </FormLabel>
                        <FormControl>
                            <Input
                                type="number"
                                placeholder={`Enter ${field.label.toLowerCase()}`}
                                {...formField}
                                onChange={(e) => {
                                    const val = e.target.value === '' ? '' : Number(e.target.value);
                                    formField.onChange(val);
                                    onChange?.(val);
                                }}
                                min={field.min_value ?? undefined}
                                max={field.max_value ?? undefined}
                                disabled={field.is_autofilled}
                            />
                        </FormControl>
                        {field.min_value !== null || field.max_value !== null ? (
                            <FormDescription>
                                {field.min_value !== null && field.max_value !== null
                                    ? `Range: ${field.min_value} - ${field.max_value}`
                                    : field.min_value !== null
                                    ? `Minimum: ${field.min_value}`
                                    : `Maximum: ${field.max_value}`}
                            </FormDescription>
                        ) : null}
                        <FormMessage />
                    </FormItem>
                )}
            />
        );
    }

    // Handle text fields (default)
    const isTextarea = field.validation.toLowerCase().includes('multiline') || 
                       field.label.toLowerCase().includes('description') ||
                       field.label.toLowerCase().includes('body') ||
                       field.label.toLowerCase().includes('notes');

    return (
        <FormField
            control={control}
            name={field.name}
            rules={isRequired ? {
                required: `${field.label} is required`,
            } : {}}
            render={({ field: formField }) => (
                <FormItem>
                    <FormLabel className="flex items-center gap-2">
                        {field.label}
                        {isRequired && <span className="text-destructive">*</span>}
                    </FormLabel>
                    <FormControl>
                        {isTextarea ? (
                            <Textarea
                                placeholder={`Enter ${field.label.toLowerCase()}`}
                                {...formField}
                                onChange={(e) => {
                                    formField.onChange(e.target.value);
                                    onChange?.(e.target.value);
                                }}
                                disabled={field.is_autofilled}
                                rows={4}
                            />
                        ) : (
                            <Input
                                type="text"
                                placeholder={`Enter ${field.label.toLowerCase()}`}
                                {...formField}
                                onChange={(e) => {
                                    formField.onChange(e.target.value);
                                    onChange?.(e.target.value);
                                }}
                                disabled={field.is_autofilled}
                            />
                        )}
                    </FormControl>
                    {field.is_autofilled && (
                        <FormDescription>
                            This field is automatically filled from your profile
                        </FormDescription>
                    )}
                    <FormMessage />
                </FormItem>
            )}
        />
    );
};

