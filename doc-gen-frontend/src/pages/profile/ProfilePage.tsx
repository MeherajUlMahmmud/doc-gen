import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { User, Shield, FileSignature } from 'lucide-react';
import { SignatureSetup } from './SignatureSetupPage';
import { GeneralTab } from './GeneralTabPage';

export const ProfilePage: React.FC = () => {
    const { user } = useAuth();

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
                        <GeneralTab />
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
