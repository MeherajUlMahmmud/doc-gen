import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '@/context/AuthContext';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { Button } from '@/components/ui/button';
import { Form } from '@/components/ui/form';
import { FormField } from '@/components/common/FormField';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { loginSchema, type LoginFormData } from '@/schemas/auth.schema';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import { ROUTES } from '@/constants/urls';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      setError(null);
      setIsLoading(true);

      await login(data);

      toast.success('Login successful');

      // Redirect to the page they were trying to access or dashboard
      const from = (location.state as any)?.from?.pathname || ROUTES.HOME;
      navigate(from, { replace: true });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      description="Enter your credentials to access your account"
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          {error && <ErrorAlert message={error} />}

          <FormField
            control={form.control}
            name="email"
            label="Email"
            type="email"
            placeholder="Enter your email"
            disabled={isLoading}
          />

          <FormField
            control={form.control}
            name="password"
            label="Password"
            type="password"
            placeholder="Enter your password"
            disabled={isLoading}
          />

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Sign In
          </Button>

          <div className="text-center text-sm">
            <span className="text-muted-foreground">Don't have an account? </span>
            <Link to={ROUTES.REGISTER} className="text-primary hover:underline font-medium">
              Sign up
            </Link>
          </div>
        </form>
      </Form>
    </AuthLayout>
  );
};
