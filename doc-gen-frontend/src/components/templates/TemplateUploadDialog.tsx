import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Upload, FileText, Loader2 } from 'lucide-react';
import { documentService } from '@/services/documents';
import { toast } from 'sonner';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import type { Template } from '@/types/document';

interface TemplateUploadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export const TemplateUploadDialog: React.FC<TemplateUploadDialogProps> = ({
  open,
  onOpenChange,
  onSuccess,
}) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadType, setUploadType] = useState<'new' | 'version'>('new');
  const [parentTemplateId, setParentTemplateId] = useState<string>('');
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loadingTemplates, setLoadingTemplates] = useState(false);

  // Load templates when upload type is 'version'
  useEffect(() => {
    const loadTemplates = async () => {
      if (uploadType === 'version' && open) {
        setLoadingTemplates(true);
        try {
          const result = await documentService.getTemplates({ is_active: true, page_size: 100 });
          // Filter to show only parent templates (version 1 or those without parent)
          const parentTemplates = result.data.filter(t => !t.parent || t.version === 1);
          setTemplates(parentTemplates);
        } catch (err) {
          toast.error('Failed to load templates');
        } finally {
          setLoadingTemplates(false);
        }
      }
    };

    loadTemplates();
  }, [uploadType, open]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      if (!selectedFile.name.endsWith('.docx')) {
        toast.error('Please select a .docx file');
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      toast.error('Please enter a template title');
      return;
    }

    if (!file) {
      toast.error('Please select a file');
      return;
    }

    if (uploadType === 'version' && !parentTemplateId) {
      toast.error('Please select a parent template');
      return;
    }

    try {
      setUploading(true);

      const formData = new FormData();
      formData.append('title', title.trim());
      formData.append('description', description.trim());
      formData.append('file', file);
      formData.append('upload_type', uploadType);

      if (uploadType === 'version' && parentTemplateId) {
        formData.append('parent_template_id', parentTemplateId);
      }

      await documentService.uploadTemplate(formData);

      const successMessage = uploadType === 'version'
        ? 'New version uploaded successfully'
        : 'Template uploaded successfully';
      toast.success(successMessage);
      onOpenChange(false);
      resetForm();
      onSuccess?.();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload template';
      toast.error(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setFile(null);
    setUploadType('new');
    setParentTemplateId('');
    setTemplates([]);
  };

  const handleClose = () => {
    if (!uploading) {
      onOpenChange(false);
      resetForm();
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Upload Template</DialogTitle>
          <DialogDescription>
            Upload a new document template or create a new version of an existing template (.docx file).
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-3">
              <Label>Upload Type <span className="text-red-500">*</span></Label>
              <RadioGroup
                value={uploadType}
                onValueChange={(value: 'new' | 'version') => {
                  setUploadType(value);
                  setParentTemplateId('');
                }}
                disabled={uploading}
                className="flex gap-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="new" id="new" />
                  <Label htmlFor="new" className="font-normal cursor-pointer">
                    New Template
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="version" id="version" />
                  <Label htmlFor="version" className="font-normal cursor-pointer">
                    New Version
                  </Label>
                </div>
              </RadioGroup>
            </div>

            {uploadType === 'version' && (
              <div className="grid gap-2">
                <Label htmlFor="parentTemplate">
                  Select Template <span className="text-red-500">*</span>
                </Label>
                <Select
                  value={parentTemplateId}
                  onValueChange={setParentTemplateId}
                  disabled={uploading || loadingTemplates}
                  required={uploadType === 'version'}
                >
                  <SelectTrigger id="parentTemplate">
                    <SelectValue placeholder={loadingTemplates ? "Loading templates..." : "Select a template"} />
                  </SelectTrigger>
                  <SelectContent>
                    {templates.map((template) => (
                      <SelectItem key={template.id} value={template.id}>
                        {template.title} (v{template.version})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {loadingTemplates && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    <span>Loading templates...</span>
                  </div>
                )}
              </div>
            )}

            <div className="grid gap-2">
              <Label htmlFor="title">
                Template Title <span className="text-red-500">*</span>
              </Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter template title"
                disabled={uploading}
                required
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter template description (optional)"
                disabled={uploading}
                rows={3}
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="file">
                Template File (.docx) <span className="text-red-500">*</span>
              </Label>
              <div className="flex items-center gap-2">
                <Input
                  id="file"
                  type="file"
                  accept=".docx"
                  onChange={handleFileChange}
                  disabled={uploading}
                  required
                />
              </div>
              {file && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <FileText className="h-4 w-4" />
                  <span>{file.name}</span>
                </div>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={uploading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={uploading}>
              {uploading ? (
                <>
                  <Upload className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Template
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
