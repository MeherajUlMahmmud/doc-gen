import { z } from 'zod';

/**
 * Profile update validation schema
 */
export const profileUpdateSchema = z.object({
  first_name: z
    .string()
    .min(1, 'First name is required')
    .max(150, 'First name is too long'),
  last_name: z
    .string()
    .min(1, 'Last name is required')
    .max(150, 'Last name is too long'),
  designation: z
    .string()
    .max(255, 'Designation is too long')
    .optional()
    .or(z.literal('')),
  division: z
    .string()
    .max(255, 'Division is too long')
    .optional()
    .or(z.literal('')),
});

export type ProfileUpdateFormData = z.infer<typeof profileUpdateSchema>;

/**
 * Profile picture validation
 */
export const profilePictureSchema = z.object({
  profile_picture: z
    .instanceof(File, { message: 'Please select a file' })
    .refine((file) => file.size <= 5 * 1024 * 1024, {
      message: 'File size must be less than 5MB',
    })
    .refine((file) => file.type.startsWith('image/'), {
      message: 'File must be an image',
    }),
});

export type ProfilePictureFormData = z.infer<typeof profilePictureSchema>;

/**
 * PIN setup validation schema
 */
export const pinSetupSchema = z.object({
  pin: z
    .string()
    .min(4, 'PIN must be at least 4 characters')
    .max(20, 'PIN is too long'),
});

export type PINSetupFormData = z.infer<typeof pinSetupSchema>;

/**
 * Signature file validation
 */
export const signatureUploadSchema = z.object({
  signature_file: z
    .instanceof(File, { message: 'Please select a file' })
    .refine((file) => file.size <= 5 * 1024 * 1024, {
      message: 'File size must be less than 5MB',
    })
    .refine((file) => file.type.startsWith('image/'), {
      message: 'File must be an image',
    }),
});

export type SignatureUploadFormData = z.infer<typeof signatureUploadSchema>;
