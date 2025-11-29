import React, { useState, useEffect } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { DocumentCard } from '@/components/documents/DocumentCard';
import { DocumentPreview } from '@/components/documents/DocumentPreview';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { Search, Plus, FileText } from 'lucide-react';
import { ROUTES } from '@/constants/urls';
import { documentService } from '@/services/documents';
import type { Document, DocumentStatus } from '@/types/document';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

export const DocumentListPage: React.FC = () => {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | DocumentStatus>('all');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [deleteDocument, setDeleteDocument] = useState<Document | null>(null);

  const pageSize = 12;

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);

      const { data, total: totalCount } = await documentService.getDocuments({
        status: activeTab === 'all' ? undefined : activeTab,
        search: searchQuery || undefined,
        page,
        page_size: pageSize,
      });

      setDocuments(data);
      setTotal(totalCount);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load documents';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [page, searchQuery, activeTab]);

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    setPage(1);
  };

  const handleView = (document: Document) => {
    setSelectedDocument(document);
    setPreviewOpen(true);
  };

  const handleEdit = (document: Document) => {
    navigate(ROUTES.DOCUMENTS_EDIT(document.id));
  };

  const handleDelete = async () => {
    if (!deleteDocument) return;

    try {
      await documentService.deleteDocument(deleteDocument.id);
      toast.success('Document deleted successfully');
      setDeleteDocument(null);
      loadDocuments();
    } catch (err) {
      toast.error('Failed to delete document');
    }
  };

  const handleDownload = async (document: Document) => {
    try {
      const blob = await documentService.downloadDocument(document.id);
      const url = window.URL.createObjectURL(blob);
      const a = window.document.createElement('a');
      a.href = url;
      a.download = `${document.title}.docx`;
      window.document.body.appendChild(a);
      a.click();
      window.document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success('Document downloaded');
    } catch (err) {
      toast.error('Failed to download document');
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">My Documents</h1>
            <p className="text-muted-foreground mt-2">
              Manage your generated documents
            </p>
          </div>
          <Button onClick={() => navigate(ROUTES.TEMPLATES)}>
            <Plus className="mr-2 h-4 w-4" />
            New Document
          </Button>
        </div>

        {/* Search Bar */}
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={(value) => {
          setActiveTab(value as typeof activeTab);
          setPage(1);
        }}>
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="draft">Drafts</TabsTrigger>
            <TabsTrigger value="pending_signature">Pending</TabsTrigger>
            <TabsTrigger value="approved">Approved</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="mt-6">
            {/* Error State */}
            {error && <ErrorAlert message={error} />}

            {/* Loading State */}
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <LoadingSpinner size="lg" text="Loading documents..." />
              </div>
            ) : documents.length === 0 ? (
              /* Empty State */
              <div className="text-center py-16">
                <FileText className="h-16 w-16 mx-auto text-muted-foreground opacity-50 mb-4" />
                <h3 className="text-lg font-semibold mb-2">No documents found</h3>
                <p className="text-muted-foreground mb-4">
                  {searchQuery
                    ? `No documents match "${searchQuery}"`
                    : 'Create your first document to get started'}
                </p>
                <Button onClick={() => navigate(ROUTES.TEMPLATES)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Document
                </Button>
              </div>
            ) : (
              <>
                {/* Document Grid */}
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {documents.map((document) => (
                    <DocumentCard
                      key={document.id}
                      document={document}
                      onView={handleView}
                      onEdit={handleEdit}
                      onDelete={(doc) => setDeleteDocument(doc)}
                      onDownload={handleDownload}
                    />
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
          </TabsContent>
        </Tabs>

        {/* Document Preview Modal */}
        <DocumentPreview
          document={selectedDocument}
          open={previewOpen}
          onOpenChange={setPreviewOpen}
          onDownload={
            selectedDocument?.generated_file
              ? () => handleDownload(selectedDocument)
              : undefined
          }
        />

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={!!deleteDocument} onOpenChange={() => setDeleteDocument(null)}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Document</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete "{deleteDocument?.title}"? This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleDelete} className="bg-red-600 hover:bg-red-700">
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </AppLayout>
  );
};
