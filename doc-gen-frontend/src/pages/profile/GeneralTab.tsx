import React, { useState, useRef } from 'react';
import { useAuth } from '@/context/AuthContext';
import { userService } from '@/services/users';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Form } from '@/components/ui/form';
import { FormField } from '@/components/common/FormField';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { profileUpdateSchema, type ProfileUpdateFormData } from '@/schemas/profile.schema';
import { toast } from 'sonner';
import { Loader2, Upload, X } from 'lucide-react';

export const GeneralTab: React.FC = () => {
    const { user, refreshUser } = useAuth();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [isUploadingPicture, setIsUploadingPicture] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const form = useForm<ProfileUpdateFormData>({
        resolver: zodResolver(profileUpdateSchema),
        defaultValues: {
            first_name: user?.first_name || '',
            last_name: user?.last_name || '',
            designation: user?.designation || '',
            division: user?.division || '',
        },
    });

    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            toast.error('Please select an image file');
            return;
        }

        // Validate file size (5MB)
        if (file.size > 5 * 1024 * 1024) {
            toast.error('File size must be less than 5MB');
            return;
        }

        setSelectedFile(file);

        // Create preview URL
        const url = URL.createObjectURL(file);
        setPreviewUrl(url);
    };

    const handleCancelUpload = () => {
        setSelectedFile(null);
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
            setPreviewUrl(null);
        }
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleUploadPicture = async () => {
        if (!selectedFile) return;

        try {
            setError(null);
            setIsUploadingPicture(true);

            await userService.uploadProfilePicture(selectedFile);
            await refreshUser();

            toast.success('Profile picture updated successfully');
            handleCancelUpload();
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to upload profile picture';
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setIsUploadingPicture(false);
        }
    };

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

    return (
        <div className="space-y-6">
            {/* Profile Picture Section */}
            <Card>
                <CardHeader>
                    <CardTitle>Profile Picture</CardTitle>
                    <CardDescription>
                        Upload a new profile picture (Max 5MB, Image files only)
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {error && <ErrorAlert message={error} />}

                        <div className="flex items-center gap-6">
                            {/* Current/Preview Avatar */}
                            <Avatar className="h-24 w-24">
                                <AvatarImage
                                    src={previewUrl || user?.profile_picture}
                                    alt={user?.full_name}
                                />
                                <AvatarFallback className="text-2xl">
                                    {getInitials()}
                                </AvatarFallback>
                            </Avatar>

                            {/* Upload Controls */}
                            <div className="flex-1 space-y-3">
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileSelect}
                                    className="hidden"
                                    id="profile-picture-upload"
                                />

                                {!selectedFile ? (
                                    <Button
                                        type="button"
                                        variant="outline"
                                        onClick={() => fileInputRef.current?.click()}
                                        disabled={isUploadingPicture}
                                    >
                                        <Upload className="mr-2 h-4 w-4" />
                                        Choose Photo
                                    </Button>
                                ) : (
                                    <div className="flex gap-2">
                                        <Button
                                            type="button"
                                            onClick={handleUploadPicture}
                                            disabled={isUploadingPicture}
                                        >
                                            {isUploadingPicture && (
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            )}
                                            Upload
                                        </Button>
                                        <Button
                                            type="button"
                                            variant="outline"
                                            onClick={handleCancelUpload}
                                            disabled={isUploadingPicture}
                                        >
                                            <X className="mr-2 h-4 w-4" />
                                            Cancel
                                        </Button>
                                    </div>
                                )}

                                {selectedFile && (
                                    <p className="text-sm text-muted-foreground">
                                        Selected: {selectedFile.name}
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Profile Information Section */}
            <Card>
                <CardHeader>
                    <CardTitle>Profile Information</CardTitle>
                    <CardDescription>
                        Update your personal and professional information
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                            {error && <ErrorAlert message={error} />}

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <FormField
                                    control={form.control}
                                    name="first_name"
                                    label="First Name"
                                    type="text"
                                    placeholder="e.g., John"
                                    disabled={isLoading}
                                    description="Your first name"
                                />

                                <FormField
                                    control={form.control}
                                    name="last_name"
                                    label="Last Name"
                                    type="text"
                                    placeholder="e.g., Doe"
                                    disabled={isLoading}
                                    description="Your last name"
                                />
                            </div>

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
        </div>
    );
};
