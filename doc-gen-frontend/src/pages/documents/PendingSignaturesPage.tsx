import React, { useState, useEffect } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { DocumentCard } from '@/components/documents/DocumentCard';
import { DocumentPreview } from '@/components/documents/DocumentPreview';
import { SignatureDialog } from '@/components/documents/SignatureDialog';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { PenTool, FileSignature, AlertCircle, CheckCircle2 } from 'lucide-react';
import { documentService } from '@/services/documents';
import type { Document } from '@/types/document';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';
import { Link } from 'react-router-dom';
import { ROUTES } from '@/constants/urls';

export const PendingSignaturesPage: React.FC = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [signatureDialogOpen, setSignatureDialogOpen] = useState(false);
  const [documentToSign, setDocumentToSign] = useState<Document | null>(null);

  const loadPendingDocuments = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await documentService.getPendingSignatures();
      setDocuments(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load pending signatures';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPendingDocuments();
  }, []);

  const handleView = (document: Document) => {
    setSelectedDocument(document);
    setPreviewOpen(true);
  };

  const handleApprove = async (pin: string, totpCode?: string) => {
    if (!documentToSign) return;

    try {
      await documentService.approveDocument(documentToSign.id, {
        pin,
        totp_code: totpCode,
      });

      toast.success('Document approved and signed successfully');
      setSignatureDialogOpen(false);
      setDocumentToSign(null);
      loadPendingDocuments();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to approve document';
      toast.error(errorMessage);
      throw err;
    }
  };

  const openSignatureDialog = (document: Document) => {
    if (!user?.signature_file) {
      toast.error('Please upload a signature in your profile first');
      return;
    }

    setDocumentToSign(document);
    setSignatureDialogOpen(true);
  };

  const canSign = user?.signature_file;

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <PenTool className="h-8 w-8" />
              Pending Signatures
            </h1>
            <p className="text-muted-foreground mt-2">
              Documents awaiting your signature
            </p>
          </div>
        </div>

        {/* Alert if signature not set up */}
        {!canSign && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="flex items-center justify-between">
              <span>
                You need to upload a signature and set up a PIN before you can approve documents.
              </span>
              <Button asChild size="sm" variant="outline">
                <Link to={ROUTES.PROFILE}>Setup Signature</Link>
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Error State */}
        {error && <ErrorAlert message={error} />}

        {/* Loading State */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner size="lg" text="Loading pending signatures..." />
          </div>
        ) : documents.length === 0 ? (
          // Empty State
          <div className="text-center py-16">
            <CheckCircle2 className="h-16 w-16 mx-auto text-green-500 mb-4" />
            <h3 className="text-lg font-semibold mb-2">All caught up!</h3>
            <p className="text-muted-foreground">
              You have no documents waiting for your signature
            </p>
          </div>
        ) : (
          /* Document Grid */
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                {documents.length} {documents.length === 1 ? 'document' : 'documents'} awaiting signature
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {documents.map((document) => (
                <div key={document.id} className="relative">
                  <DocumentCard
                    document={document}
                    onView={handleView}
                  />
                  <div className="mt-3">
                    <Button
                      className="w-full"
                      onClick={() => openSignatureDialog(document)}
                      disabled={!canSign}
                    >
                      <FileSignature className="mr-2 h-4 w-4" />
                      Sign Document
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Document Preview Modal */}
        <DocumentPreview
          document={selectedDocument}
          open={previewOpen}
          onOpenChange={setPreviewOpen}
        />

        {/* Signature Dialog */}
        <SignatureDialog
          document={documentToSign}
          open={signatureDialogOpen}
          onOpenChange={setSignatureDialogOpen}
          onApprove={handleApprove}
        />
      </div>
    </AppLayout>
  );
};
