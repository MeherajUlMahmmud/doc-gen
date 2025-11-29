import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { userService } from '@/services/users';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Form } from '@/components/ui/form';
import { FormField } from '@/components/common/FormField';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { profileUpdateSchema, type ProfileUpdateFormData } from '@/schemas/profile.schema';
import { toast } from 'sonner';
import { Loader2, User, Shield, FileSignature } from 'lucide-react';
import { SignatureSetup } from './SignatureSetup';

export const ProfilePage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<ProfileUpdateFormData>({
    resolver: zodResolver(profileUpdateSchema),
    defaultValues: {
      designation: user?.designation || '',
      division: user?.division || '',
    },
  });

  const onSubmit = async (data: ProfileUpdateFormData) => {
    try {
      setError(null);
      setIsLoading(true);

      await userService.updateProfile(data);
      await refreshUser();

      toast.success('Profile updated successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update profile';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const getInitials = () => {
    if (!user) return 'U';
    return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
  };

  if (!user) {
    return (
      <AppLayout>
        <div className="flex justify-center items-center h-96">
          <LoadingSpinner size="lg" text="Loading profile..." />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Profile Header */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-4">
              <Avatar className="h-20 w-20">
                <AvatarImage src={user.profile_picture} alt={user.full_name} />
                <AvatarFallback className="text-2xl">{getInitials()}</AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <CardTitle className="text-2xl">{user.full_name}</CardTitle>
                <CardDescription className="text-base">{user.email}</CardDescription>
                <div className="mt-2 flex gap-2">
                  {user.is_verified && (
                    <Badge variant="secondary" className="gap-1">
                      <Shield className="h-3 w-3" />
                      Verified
                    </Badge>
                  )}
                  {user.is_admin && <Badge variant="destructive">Admin</Badge>}
                  {user.is_staff && !user.is_admin && <Badge variant="default">Staff</Badge>}
                </div>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Tabs */}
        <Tabs defaultValue="general" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="general" className="gap-2">
              <User className="h-4 w-4" />
              General
            </TabsTrigger>
            <TabsTrigger value="signature" className="gap-2">
              <FileSignature className="h-4 w-4" />
              Signature & Security
            </TabsTrigger>
          </TabsList>

          {/* General Tab */}
          <TabsContent value="general">
            <Card>
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>
                  Update your designation and division information
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    {error && <ErrorAlert message={error} />}

                    <FormField
                      control={form.control}
                      name="designation"
                      label="Designation"
                      type="text"
                      placeholder="e.g., Senior Manager"
                      disabled={isLoading}
                      description="Your job title or designation"
                    />

                    <FormField
                      control={form.control}
                      name="division"
                      label="Division"
                      type="text"
                      placeholder="e.g., Finance Department"
                      disabled={isLoading}
                      description="Your department or division"
                    />

                    <div className="flex justify-end">
                      <Button type="submit" disabled={isLoading}>
                        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Save Changes
                      </Button>
                    </div>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Signature & Security Tab */}
          <TabsContent value="signature">
            <SignatureSetup />
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
};
