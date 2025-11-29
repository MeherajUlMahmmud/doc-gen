import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { FileText, User, LogOut, Menu, PenTool } from 'lucide-react';
import { toast } from 'sonner';
import { ROUTES } from '@/constants/urls';

interface AppLayoutProps {
    children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

    const handleLogout = async () => {
        try {
            await logout();
            toast.success('Logged out successfully');
            navigate(ROUTES.LOGIN);
        } catch (error) {
            toast.error('Failed to logout');
        }
    };

    const getInitials = () => {
        if (!user) return 'U';
        return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    };

    return (
        <div className="flex min-h-screen flex-col">
            {/* Header */}
            <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
                <div className="container mx-auto  flex h-16 items-center justify-between">
                    <div className="flex items-center gap-6">
                        <Link to={ROUTES.HOME} className="flex items-center gap-2">
                            <FileText className="h-6 w-6" />
                            <span className="text-xl font-bold">DocGen</span>
                        </Link>

                        {/* Desktop Navigation */}
                        <nav className="hidden md:flex items-center gap-6">
                            <Link
                                to={ROUTES.TEMPLATES}
                                className="text-sm font-medium transition-colors hover:text-primary"
                            >
                                Templates
                            </Link>
                            <Link
                                to={ROUTES.DOCUMENTS}
                                className="text-sm font-medium transition-colors hover:text-primary"
                            >
                                Documents
                            </Link>
                            <Link
                                to={ROUTES.DOCUMENTS_PENDING_SIGNATURES}
                                className="text-sm font-medium transition-colors hover:text-primary flex items-center gap-1"
                            >
                                <PenTool className="h-3.5 w-3.5" />
                                Pending Signatures
                            </Link>
                        </nav>
                    </div>

                    {/* User Menu */}
                    <div className="flex items-center gap-4">
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                                    <Avatar className="h-10 w-10">
                                        <AvatarImage src={user?.profile_picture} alt={user?.full_name} />
                                        <AvatarFallback>{getInitials()}</AvatarFallback>
                                    </Avatar>
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent className="w-56" align="end" forceMount>
                                <DropdownMenuLabel className="font-normal">
                                    <div className="flex flex-col space-y-1">
                                        <p className="text-sm font-medium leading-none">{user?.full_name}</p>
                                        <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
                                    </div>
                                </DropdownMenuLabel>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem asChild>
                                    <Link to={ROUTES.PROFILE} className="cursor-pointer">
                                        <User className="mr-2 h-4 w-4" />
                                        <span>Profile</span>
                                    </Link>
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-red-600">
                                    <LogOut className="mr-2 h-4 w-4" />
                                    <span>Log out</span>
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>

                        {/* Mobile Menu Button */}
                        <Button
                            variant="ghost"
                            size="icon"
                            className="md:hidden"
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        >
                            <Menu className="h-6 w-6" />
                        </Button>
                    </div>
                </div>

                {/* Mobile Navigation */}
                {mobileMenuOpen && (
                    <div className="border-t md:hidden">
                        <nav className="container flex flex-col gap-4 py-4">
                            <Link
                                to={ROUTES.TEMPLATES}
                                className="text-sm font-medium transition-colors hover:text-primary"
                                onClick={() => setMobileMenuOpen(false)}
                            >
                                Templates
                            </Link>
                            <Link
                                to={ROUTES.DOCUMENTS}
                                className="text-sm font-medium transition-colors hover:text-primary"
                                onClick={() => setMobileMenuOpen(false)}
                            >
                                Documents
                            </Link>
                            <Link
                                to={ROUTES.DOCUMENTS_PENDING_SIGNATURES}
                                className="text-sm font-medium transition-colors hover:text-primary flex items-center gap-1"
                                onClick={() => setMobileMenuOpen(false)}
                            >
                                <PenTool className="h-3.5 w-3.5" />
                                Pending Signatures
                            </Link>
                        </nav>
                    </div>
                )}
            </header>

            {/* Main Content */}
            <main className="flex-1 container py-6 mx-auto ">{children}</main>

            {/* Footer */}
            <footer className="border-t py-6">
                <div className="container mx-auto text-center text-sm text-muted-foreground">
                    © {new Date().getFullYear()} Document Generator. All rights reserved.
                </div>
            </footer>
        </div>
    );
};
