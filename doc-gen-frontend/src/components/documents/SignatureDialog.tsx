import React, { useState } from 'react';
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
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Loader2, CheckCircle2, AlertCircle, FileSignature } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import type { Document } from '@/types/document';

interface SignatureDialogProps {
  document: Document | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onApprove: (pin: string, totpCode?: string) => Promise<void>;
}

export const SignatureDialog: React.FC<SignatureDialogProps> = ({
  document,
  open,
  onOpenChange,
  onApprove,
}) => {
  const { user } = useAuth();
  const [pin, setPin] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!pin) {
      setError('Please enter your PIN');
      return;
    }

    if (user?.two_factor_enabled && !totpCode) {
      setError('Please enter your 2FA code');
      return;
    }

    try {
      setIsSubmitting(true);
      await onApprove(pin, user?.two_factor_enabled ? totpCode : undefined);
      // Reset form on success
      setPin('');
      setTotpCode('');
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve document');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setPin('');
    setTotpCode('');
    setError(null);
    onOpenChange(false);
  };

  if (!document) return null;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileSignature className="h-5 w-5" />
            Approve Document
          </DialogTitle>
          <DialogDescription>
            You are about to sign and approve: <strong>{document.title}</strong>
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Show User's Signature */}
          {user?.signature_file && (
            <div className="border rounded-lg p-4 bg-muted/50">
              <Label className="text-sm text-muted-foreground mb-2 block">
                Your Signature:
              </Label>
              <div className="bg-white border rounded p-2 flex items-center justify-center">
                <img
                  src={user.signature_file}
                  alt="Your signature"
                  className="max-h-16 object-contain"
                />
              </div>
            </div>
          )}

          {!user?.signature_file && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                You haven't uploaded a signature yet. Please upload one in your profile.
              </AlertDescription>
            </Alert>
          )}

          <Separator />

          {/* PIN Input */}
          <div className="space-y-2">
            <Label htmlFor="pin">
              Signature PIN <span className="text-red-500">*</span>
            </Label>
            <Input
              id="pin"
              type="password"
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              placeholder="Enter your signature PIN"
              disabled={isSubmitting || !user?.signature_file}
              required
            />
            <p className="text-xs text-muted-foreground">
              Enter the PIN you set up for signature authentication
            </p>
          </div>

          {/* 2FA Code Input (if enabled) */}
          {user?.two_factor_enabled && (
            <div className="space-y-2">
              <Label htmlFor="totp">
                2FA Code <span className="text-red-500">*</span>
              </Label>
              <Input
                id="totp"
                type="text"
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value)}
                placeholder="Enter 6-digit code"
                maxLength={6}
                disabled={isSubmitting || !user?.signature_file}
                required
              />
              <p className="text-xs text-muted-foreground">
                Enter the code from your authenticator app
              </p>
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting || !user?.signature_file}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Approving...
                </>
              ) : (
                <>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  Approve & Sign
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
