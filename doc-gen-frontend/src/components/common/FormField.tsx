import React from 'react';
import {
  FormControl,
  FormDescription,
  FormField as ShadcnFormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Control, FieldPath, FieldValues } from 'react-hook-form';

interface BaseFormFieldProps<T extends FieldValues> {
  control: Control<T>;
  name: FieldPath<T>;
  label?: string;
  description?: string;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

interface InputFormFieldProps<T extends FieldValues> extends BaseFormFieldProps<T> {
  type?: 'text' | 'email' | 'password' | 'number';
  variant?: 'input';
}

interface TextareaFormFieldProps<T extends FieldValues> extends BaseFormFieldProps<T> {
  variant: 'textarea';
  rows?: number;
}

type FormFieldProps<T extends FieldValues> =
  | InputFormFieldProps<T>
  | TextareaFormFieldProps<T>;

export function FormField<T extends FieldValues>({
  control,
  name,
  label,
  description,
  placeholder,
  disabled,
  className,
  ...props
}: FormFieldProps<T>) {
  return (
    <ShadcnFormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          {label && <FormLabel>{label}</FormLabel>}
          <FormControl>
            {props.variant === 'textarea' ? (
              <Textarea
                placeholder={placeholder}
                disabled={disabled}
                rows={props.rows}
                {...field}
              />
            ) : (
              <Input
                type={props.type || 'text'}
                placeholder={placeholder}
                disabled={disabled}
                {...field}
              />
            )}
          </FormControl>
          {description && <FormDescription>{description}</FormDescription>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
