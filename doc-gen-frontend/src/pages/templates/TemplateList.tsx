import React, { useState, useEffect } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { TemplateCard } from '@/components/documents/TemplateCard';
import { TemplateUploadDialog } from '@/components/templates/TemplateUploadDialog';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { Search, Plus, FileText } from 'lucide-react';
import { documentService } from '@/services/documents';
import type { Template } from '@/types/document';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';

export const TemplateListPage: React.FC = () => {
    const { user } = useAuth();
    const [templates, setTemplates] = useState<Template[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const [uploadDialogOpen, setUploadDialogOpen] = useState(false);

    const pageSize = 12;

    const loadTemplates = async () => {
        try {
            setLoading(true);
            setError(null);

            const { data, total: totalCount } = await documentService.getTemplates({
                search: searchQuery || undefined,
                is_active: true,
                page,
                page_size: pageSize,
            });

            setTemplates(data);
            setTotal(totalCount);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to load templates';
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadTemplates();
    }, [page, searchQuery]);

    const handleSearch = (value: string) => {
        setSearchQuery(value);
        setPage(1);
    };

    const totalPages = Math.ceil(total / pageSize);

    return (
        <AppLayout>
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold">Templates</h1>
                        <p className="text-muted-foreground mt-2">
                            Browse available document templates
                        </p>
                    </div>
                    {user?.is_admin && (
                        <Button onClick={() => setUploadDialogOpen(true)}>
                            <Plus className="mr-2 h-4 w-4" />
                            Upload Template
                        </Button>
                    )}
                </div>

                {/* Search Bar */}
                <div className="relative max-w-md">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search templates..."
                        value={searchQuery}
                        onChange={(e) => handleSearch(e.target.value)}
                        className="pl-10"
                    />
                </div>

                {/* Error State */}
                {error && <ErrorAlert message={error} />}

                {/* Loading State */}
                {loading ? (
                    <div className="flex justify-center items-center h-64">
                        <LoadingSpinner size="lg" text="Loading templates..." />
                    </div>
                ) : templates.length === 0 ? (
                    /* Empty State */
                    <div className="text-center py-16">
                        <FileText className="h-16 w-16 mx-auto text-muted-foreground opacity-50 mb-4" />
                        <h3 className="text-lg font-semibold mb-2">No templates found</h3>
                        <p className="text-muted-foreground">
                            {searchQuery
                                ? `No templates match "${searchQuery}"`
                                : 'No templates available at the moment'}
                        </p>
                    </div>
                ) : (
                    <>
                        {/* Template Grid */}
                        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                            {templates.map((template) => (
                                <TemplateCard key={template.id} template={template} />
                            ))}
                        </div>

                        {/* Pagination */}
                        {totalPages > 1 && (
                            <div className="flex justify-center gap-2 mt-8">
                                <Button
                                    variant="outline"
                                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                                    disabled={page === 1}
                                >
                                    Previous
                                </Button>
                                <div className="flex items-center gap-2 px-4">
                                    <span className="text-sm text-muted-foreground">
                                        Page {page} of {totalPages}
                                    </span>
                                </div>
                                <Button
                                    variant="outline"
                                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                                    disabled={page === totalPages}
                                >
                                    Next
                                </Button>
                            </div>
                        )}
                    </>
                )}

                {/* Upload Template Dialog */}
                <TemplateUploadDialog
                    open={uploadDialogOpen}
                    onOpenChange={setUploadDialogOpen}
                    onSuccess={loadTemplates}
                />
            </div>
        </AppLayout>
    );
};
