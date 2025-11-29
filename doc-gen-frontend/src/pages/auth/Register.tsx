import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '@/context/AuthContext';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { Button } from '@/components/ui/button';
import { Form } from '@/components/ui/form';
import { FormField } from '@/components/common/FormField';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { registerSchema, type RegisterFormData } from '@/schemas/auth.schema';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import { ROUTES } from '@/constants/urls';

export const RegisterPage: React.FC = () => {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      password_confirm: '',
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setError(null);
      setIsLoading(true);

      await registerUser(data);

      toast.success('Registration successful! Please login to continue.');
      navigate(ROUTES.LOGIN);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Registration failed';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Create an account"
      description="Enter your information to get started"
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          {error && <ErrorAlert message={error} />}

          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="first_name"
              label="First Name"
              type="text"
              placeholder="John"
              disabled={isLoading}
            />

            <FormField
              control={form.control}
              name="last_name"
              label="Last Name"
              type="text"
              placeholder="Doe"
              disabled={isLoading}
            />
          </div>

          <FormField
            control={form.control}
            name="email"
            label="Email"
            type="email"
            placeholder="john.doe@example.com"
            disabled={isLoading}
          />

          <FormField
            control={form.control}
            name="password"
            label="Password"
            type="password"
            placeholder="Create a password"
            disabled={isLoading}
            description="Must be at least 8 characters with uppercase, lowercase, and number"
          />

          <FormField
            control={form.control}
            name="password_confirm"
            label="Confirm Password"
            type="password"
            placeholder="Confirm your password"
            disabled={isLoading}
          />

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Create Account
          </Button>

          <div className="text-center text-sm">
            <span className="text-muted-foreground">Already have an account? </span>
            <Link to={ROUTES.LOGIN} className="text-primary hover:underline font-medium">
              Sign in
            </Link>
          </div>
        </form>
      </Form>
    </AuthLayout>
  );
};
