import React, { useState, useRef } from 'react';
import { useAuth } from '@/context/AuthContext';
import { userService } from '@/services/users';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { toast } from 'sonner';
import {
  Upload,
  FileSignature,
  Lock,
  Shield,
  Loader2,
  CheckCircle2,
  XCircle
} from 'lucide-react';

export const SignatureSetup: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [isUploadingSignature, setIsUploadingSignature] = useState(false);
  const [isSettingPIN, setIsSettingPIN] = useState(false);
  const [is2FALoading, setIs2FALoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pin, setPin] = useState('');
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [secret, setSecret] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSignatureUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file
    if (!file.type.startsWith('image/')) {
      toast.error('Please select an image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be less than 5MB');
      return;
    }

    try {
      setError(null);
      setIsUploadingSignature(true);

      await userService.uploadSignature(file);
      await refreshUser();

      toast.success('Signature uploaded successfully');

      // Clear the input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload signature';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsUploadingSignature(false);
    }
  };

  const handlePINSetup = async () => {
    if (pin.length < 4) {
      toast.error('PIN must be at least 4 characters');
      return;
    }

    try {
      setError(null);
      setIsSettingPIN(true);

      await userService.setupPIN({ pin });
      await refreshUser();

      toast.success('PIN set successfully');
      setPin('');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to set PIN';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsSettingPIN(false);
    }
  };

  const handle2FASetup = async () => {
    try {
      setError(null);
      setIs2FALoading(true);

      if (!user?.two_factor_enabled) {
        // Enable 2FA and get QR code
        const response = await userService.toggle2FA({ action: 'enable' });
        setQrCode(response.qr_code || null);
        setSecret(response.secret || null);
        await refreshUser();
        toast.success('2FA enabled successfully');
      } else {
        // Disable 2FA
        await userService.toggle2FA({ action: 'disable' });
        setQrCode(null);
        setSecret(null);
        await refreshUser();
        toast.success('2FA disabled successfully');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to toggle 2FA';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIs2FALoading(false);
    }
  };

  const handleGet2FAQRCode = async () => {
    try {
      setError(null);
      setIs2FALoading(true);

      const response = await userService.get2FAQRCode();
      setQrCode(response.qr_code || null);
      setSecret(response.secret || null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get QR code';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIs2FALoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {error && <ErrorAlert message={error} />}

      {/* Signature Upload */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileSignature className="h-5 w-5" />
                Signature Upload
              </CardTitle>
              <CardDescription>
                Upload your digital signature for document signing
              </CardDescription>
            </div>
            {user?.signature_file && (
              <Badge variant="secondary" className="gap-1">
                <CheckCircle2 className="h-3 w-3" />
                Uploaded
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {user?.signature_file && (
            <div className="border rounded-lg p-4 bg-muted/50">
              <p className="text-sm text-muted-foreground mb-2">Current signature:</p>
              <img
                src={user.signature_file}
                alt="Your signature"
                className="max-h-24 border rounded bg-white"
              />
            </div>
          )}

          <div>
            <Label htmlFor="signature-upload">Upload New Signature</Label>
            <div className="mt-2 flex gap-2">
              <Input
                id="signature-upload"
                type="file"
                accept="image/*"
                ref={fileInputRef}
                onChange={handleSignatureUpload}
                disabled={isUploadingSignature}
                className="flex-1"
              />
              <Button
                variant="outline"
                disabled={isUploadingSignature}
                onClick={() => fileInputRef.current?.click()}
              >
                {isUploadingSignature ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Upload className="h-4 w-4" />
                )}
              </Button>
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Maximum file size: 5MB. Accepted formats: JPG, PNG, GIF
            </p>
          </div>
        </CardContent>
      </Card>

      {/* PIN Setup */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Lock className="h-5 w-5" />
                Signature PIN
              </CardTitle>
              <CardDescription>
                Set a PIN to protect your signature
              </CardDescription>
            </div>
            <Badge variant="secondary" className="gap-1">
              <CheckCircle2 className="h-3 w-3" />
              {/* Always show as "Set" since we can't retrieve the actual PIN */}
              PIN Configured
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert>
            <AlertDescription className="text-sm">
              {user?.signature_file
                ? 'Your signature PIN is configured. Enter a new PIN to update it.'
                : 'Set up a PIN to protect your signature. This PIN will be required when signing documents.'}
            </AlertDescription>
          </Alert>

          <div>
            <Label htmlFor="pin">
              {user?.signature_file ? 'New PIN (minimum 4 characters)' : 'PIN (minimum 4 characters)'}
            </Label>
            <div className="mt-2 flex gap-2">
              <Input
                id="pin"
                type="password"
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                placeholder={user?.signature_file ? "Enter new PIN" : "Enter your PIN"}
                disabled={isSettingPIN}
                className="flex-1"
              />
              <Button
                onClick={handlePINSetup}
                disabled={isSettingPIN || pin.length < 4}
              >
                {isSettingPIN ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : null}
                {user?.signature_file ? 'Update PIN' : 'Set PIN'}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Your PIN is securely hashed and cannot be retrieved. You can only set a new one.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 2FA Setup */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Two-Factor Authentication
              </CardTitle>
              <CardDescription>
                Add an extra layer of security to your signature
              </CardDescription>
            </div>
            {user?.two_factor_enabled ? (
              <Badge variant="default" className="gap-1">
                <CheckCircle2 className="h-3 w-3" />
                Enabled
              </Badge>
            ) : (
              <Badge variant="secondary" className="gap-1">
                <XCircle className="h-3 w-3" />
                Disabled
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {user?.two_factor_enabled ? (
            <Alert>
              <AlertDescription>
                Two-factor authentication is currently enabled for your signature.
              </AlertDescription>
            </Alert>
          ) : (
            <Alert>
              <AlertDescription>
                Enable 2FA to require an authentication code when signing documents.
              </AlertDescription>
            </Alert>
          )}

          <div className="flex gap-2">
            <Button
              onClick={handle2FASetup}
              disabled={is2FALoading}
              variant={user?.two_factor_enabled ? 'destructive' : 'default'}
            >
              {is2FALoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {user?.two_factor_enabled ? 'Disable 2FA' : 'Enable 2FA'}
            </Button>

            {user?.two_factor_enabled && (
              <Button
                onClick={handleGet2FAQRCode}
                disabled={is2FALoading}
                variant="outline"
              >
                {is2FALoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Show QR Code
              </Button>
            )}
          </div>

          {qrCode && (
            <div className="border rounded-lg p-4 space-y-4">
              <div>
                <p className="text-sm font-medium mb-2">
                  Scan this QR code with your authenticator app:
                </p>
                <img
                  src={qrCode}
                  alt="2FA QR Code"
                  className="max-w-xs mx-auto border rounded bg-white p-2"
                />
              </div>

              {secret && (
                <div>
                  <Separator className="my-4" />
                  <p className="text-sm font-medium mb-2">
                    Or enter this secret key manually:
                  </p>
                  <code className="block bg-muted p-2 rounded text-sm font-mono break-all">
                    {secret}
                  </code>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
