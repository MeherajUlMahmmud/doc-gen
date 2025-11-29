import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { Download, FileText } from 'lucide-react';
import type { Document, DocumentStatus } from '@/types/document';
import { format } from 'date-fns';

interface DocumentPreviewProps {
  document: Document | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDownload?: () => void;
}

const statusConfig: Record<DocumentStatus, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
  draft: { label: 'Draft', variant: 'secondary' },
  pending_signature: { label: 'Pending Signature', variant: 'outline' },
  approved: { label: 'Approved', variant: 'default' },
  rejected: { label: 'Rejected', variant: 'destructive' },
};

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  document,
  open,
  onOpenChange,
  onDownload,
}) => {
  if (!document) return null;

  const status = statusConfig[document.status] || statusConfig.draft;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <FileText className="h-6 w-6 text-primary" />
            <div className="flex-1">
              <DialogTitle>{document.title}</DialogTitle>
              <DialogDescription>
                Template: {document.template.name}
              </DialogDescription>
            </div>
            <Badge variant={status.variant}>{status.label}</Badge>
          </div>
        </DialogHeader>

        <div className="space-y-4">
          {/* Document Info */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Created</p>
              <p className="font-medium">
                {format(new Date(document.created_at), 'PPP')}
              </p>
            </div>
            {document.approved_at && (
              <div>
                <p className="text-muted-foreground">Approved</p>
                <p className="font-medium">
                  {format(new Date(document.approved_at), 'PPP')}
                </p>
              </div>
            )}
          </div>

          <Separator />

          {/* Document Fields */}
          <div>
            <h3 className="font-semibold mb-3">Document Fields</h3>
            <div className="space-y-3">
              {Object.entries(document.fields).length > 0 ? (
                Object.entries(document.fields).map(([key, value]) => (
                  <div key={key} className="grid grid-cols-3 gap-4 text-sm">
                    <p className="text-muted-foreground font-medium capitalize">
                      {key.replace(/_/g, ' ')}:
                    </p>
                    <p className="col-span-2">
                      {typeof value === 'boolean'
                        ? value
                          ? 'Yes'
                          : 'No'
                        : String(value)}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No fields available</p>
              )}
            </div>
          </div>

          {/* Download Button */}
          {document.generated_file && onDownload && (
            <>
              <Separator />
              <Button onClick={onDownload} className="w-full">
                <Download className="mr-2 h-4 w-4" />
                Download Document
              </Button>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
