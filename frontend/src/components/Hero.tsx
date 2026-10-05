import { useState, useRef } from 'react';
import { Image as ImageIcon, Link as LinkIcon, FileText, UploadCloud, X, Clipboard, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';

export default function Hero({ onRun }: any) {
  const [tab, setTab] = useState<'text' | 'url' | 'qr'>('text');
  const [input, setInput] = useState('');
  const [qrFile, setQrFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleQrSelection = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setValidationError('Please upload a valid image file (PNG, JPG, WebP).');
      return;
    }
    setValidationError(null);
    setQrFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const clearQr = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setQrFile(null);
    setPreviewUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleQrSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleQrSelection(e.target.files[0]);
    }
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setInput(text);
        setValidationError(null);
      }
    } catch {
      // Browser permissions fallback
    }
  };

  const handleSubmit = () => {
    if (tab === 'qr') {
      if (!qrFile) {
        setValidationError('Please upload or drop a QR code image to analyze.');
        return;
      }
      setValidationError(null);
      onRun('qr', qrFile);
    } else if (tab === 'url') {
      const trimmed = input.trim();
      if (!trimmed) {
        setValidationError('Please enter a URL or web domain to analyze.');
        return;
      }
      setValidationError(null);
      onRun('url', trimmed.startsWith('http') ? trimmed : `https://${trimmed}`);
    } else {
      const trimmed = input.trim();
      if (!trimmed) {
        setValidationError('Please paste an SMS, message, or payment request to analyze.');
        return;
      }
      setValidationError(null);
      onRun('text', trimmed);
    }
  };

  return (
    <div className="flex flex-col items-center text-center mt-2 mb-2 gap-4">
      <div className="max-w-2xl">
        <h2 className="text-3xl md:text-5xl font-display font-bold mb-2">Is that payment request lying to you?</h2>
        <p className="text-base md:text-lg text-text-muted">Paste a message, link, or QR — VeriFi investigates the evidence, not the vibes.</p>
      </div>

      <div className="glass-panel w-full max-w-3xl p-1 flex flex-col gap-2">
        <div className="flex items-center justify-between border-b border-border-glass p-1">
          <div className="flex items-center gap-2">
            <button 
              onClick={() => { setTab('text'); setValidationError(null); }} 
              className={clsx("flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors", tab==='text' ? "bg-black/10 dark:bg-white/10 text-text-primary":"text-text-muted hover:text-text-primary")}
            >
              <FileText size={16}/> Text Message
            </button>
            <button 
              onClick={() => { setTab('url'); setValidationError(null); }} 
              className={clsx("flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors", tab==='url' ? "bg-black/10 dark:bg-white/10 text-text-primary":"text-text-muted hover:text-text-primary")}
            >
              <LinkIcon size={16}/> URL Link
            </button>
            <button 
              onClick={() => { setTab('qr'); setValidationError(null); }} 
              className={clsx("flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors", tab==='qr' ? "bg-black/10 dark:bg-white/10 text-text-primary":"text-text-muted hover:text-text-primary")}
            >
              <ImageIcon size={16}/> QR Code
            </button>
          </div>

          {tab === 'text' && (
            <button 
              onClick={handlePaste}
              className="flex items-center gap-1.5 text-xs text-text-muted hover:text-blue-400 px-2.5 py-1 rounded border border-border-glass hover:bg-white/5 transition-colors"
              title="Paste from clipboard"
            >
              <Clipboard size={14}/> Paste
            </button>
          )}
        </div>
        
        <div className="p-3 min-h-[130px] flex items-center justify-center">
          {tab === 'text' && (
            <div className="w-full flex flex-col">
              <textarea 
                className="w-full h-24 bg-transparent border-none outline-none resize-none text-lg text-text-primary placeholder:text-text-muted/50" 
                placeholder="Paste the suspicious SMS, WhatsApp message, or UPI request here..." 
                value={input} 
                onChange={e => { setInput(e.target.value); setValidationError(null); }} 
              />
              <div className="flex justify-between items-center text-xs text-text-muted pt-2 border-t border-white/5 font-mono">
                <span>Enter text containing payment claims, UPI IDs, or urgency requests</span>
                <span>{input.length} chars</span>
              </div>
            </div>
          )}

          {tab === 'url' && (
            <div className="w-full flex flex-col gap-3">
              <input 
                type="text" 
                className="w-full bg-transparent border-b border-border-glass pb-2 outline-none text-xl text-center font-mono placeholder:text-text-muted/40 focus:border-blue-500 transition-colors" 
                placeholder="e.g. sbi-kyc-verify.com/login" 
                value={input} 
                onChange={e => { setInput(e.target.value); setValidationError(null); }} 
                onKeyDown={e => e.key === 'Enter' && handleSubmit()}
              />
              <div className="flex items-center justify-center gap-2 flex-wrap text-xs text-text-muted font-mono">
                <span>Quick samples:</span>
                <button 
                  type="button" 
                  onClick={() => { setInput('sbi-kyc-verify.com'); setValidationError(null); }} 
                  className="px-2 py-0.5 rounded bg-white/5 hover:bg-white/10 hover:text-text-primary transition-colors border border-border-glass"
                >
                  sbi-kyc-verify.com
                </button>
                <button 
                  type="button" 
                  onClick={() => { setInput('bijli-bill-pay.in'); setValidationError(null); }} 
                  className="px-2 py-0.5 rounded bg-white/5 hover:bg-white/10 hover:text-text-primary transition-colors border border-border-glass"
                >
                  bijli-bill-pay.in
                </button>
              </div>
            </div>
          )}

          {tab === 'qr' && (
            <div 
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={clsx(
                "w-full min-h-[110px] border-2 border-dashed rounded-xl flex items-center justify-center transition-all cursor-pointer p-4",
                isDragging ? "border-blue-500 bg-blue-500/10 scale-[1.01]" : "border-border-glass hover:border-blue-500/50 hover:bg-white/5",
                previewUrl ? "border-emerald-500/40 bg-emerald-500/5" : ""
              )}
            >
              <input type="file" ref={fileInputRef} className="hidden" accept="image/*" onChange={handleFileChange} />
              {previewUrl && qrFile ? (
                <div className="flex items-center gap-4 w-full justify-between">
                  <div className="flex items-center gap-3">
                    <img src={previewUrl} alt="QR Preview" className="w-16 h-16 object-contain rounded-lg border border-white/10 bg-black/40 p-1" />
                    <div className="flex flex-col text-left">
                      <span className="font-medium text-sm text-text-primary truncate max-w-[200px] sm:max-w-xs">{qrFile.name}</span>
                      <span className="text-xs text-text-muted font-mono">{(qrFile.size / 1024).toFixed(1)} KB • Image ready for decoding</span>
                    </div>
                  </div>
                  <button 
                    type="button" 
                    onClick={clearQr} 
                    className="p-1.5 rounded-lg bg-white/10 hover:bg-red-500/20 hover:text-red-400 text-text-muted transition-colors"
                    title="Remove QR image"
                  >
                    <X size={18}/>
                  </button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-1.5 text-text-muted">
                  <UploadCloud size={28} className={isDragging ? "text-blue-400 animate-bounce" : "opacity-60"} />
                  <span className="text-sm font-medium">Drop QR image here or click to browse</span>
                  <span className="text-xs opacity-60">Supports UPI QR codes, barcodes, and payment screenshots</span>
                </div>
              )}
            </div>
          )}
        </div>

        {validationError && (
          <div className="flex items-center gap-2 px-3 py-1.5 mx-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs text-left animate-fade-in">
            <AlertCircle size={14} className="shrink-0" />
            <span>{validationError}</span>
          </div>
        )}

        <div className="p-2">
          <button 
            type="button"
            onClick={handleSubmit} 
            className="w-full py-3 rounded-xl font-display font-bold text-lg text-white bg-[var(--accent)] shadow-[0_0_20px_rgba(99,102,241,0.4)] hover:shadow-[0_0_30px_rgba(6,182,212,0.6)] hover:scale-[0.99] active:scale-[0.98] transition-all duration-300"
          >
            Run Deep Investigation
          </button>
        </div>
      </div>
    </div>
  );
}
