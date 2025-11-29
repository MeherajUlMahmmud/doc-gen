import { z } from 'zod';

/**
 * Create a dynamic document schema based on template fields
 */
export const createDocumentSchema = (fields: Array<{ name: string; label: string; type: string; required?: boolean; validation: string; min_value?: number | null; max_value?: number | null }>) => {
    const schemaObject: Record<string, z.ZodTypeAny> = {
        title: z.string().min(2, 'Document title must be at least 2 characters').max(255, 'Document title must be less than 255 characters'),
    };

    fields.forEach((field) => {
        const isRequired = field.required || field.validation.toLowerCase().includes('required');
        
        if (field.type === 'number') {
            let numberSchema = z.number();
            
            if (field.min_value !== null && field.min_value !== undefined) {
                numberSchema = numberSchema.min(field.min_value, `Value must be at least ${field.min_value}`);
            }
            
            if (field.max_value !== null && field.max_value !== undefined) {
                numberSchema = numberSchema.max(field.max_value, `Value must be at most ${field.max_value}`);
            }
            
            if (isRequired) {
                schemaObject[field.name] = numberSchema;
            } else {
                schemaObject[field.name] = numberSchema.optional();
            }
        } else if (field.type === 'checkbox') {
            if (isRequired) {
                schemaObject[field.name] = z.boolean().refine((val) => val === true, {
                    message: `${field.label} must be checked`,
                });
            } else {
                schemaObject[field.name] = z.boolean().optional();
            }
        } else if (field.type === 'signature') {
            // Signature fields are handled during approval, so we don't validate them here
            schemaObject[field.name] = z.any().optional();
        } else {
            // Text field
            let textSchema = z.string();
            
            if (isRequired) {
                textSchema = textSchema.min(1, `${field.label} is required`);
            }
            
            schemaObject[field.name] = isRequired ? textSchema : textSchema.optional();
        }
    });

    return z.object(schemaObject);
};

/**
 * Type for document form data
 */
export type DocumentFormData = z.infer<ReturnType<typeof createDocumentSchema>>;

