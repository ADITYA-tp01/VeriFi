import { useState, useRef } from 'react';
import { Search, Image as ImageIcon, Link as LinkIcon, FileText } from 'lucide-react';
import { clsx } from 'clsx';

export default function Hero({ onRun }: any) {
  const [tab, setTab] = useState<'text'|'url'|'qr'>('text');
  const [input, setInput] = useState('');
  const [qrFile, setQrFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setQrFile(e.dataTransfer.files[0]);
    }
  };
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setQrFile(e.target.files[0]);
    }
  };

  return (
    <div className="flex flex-col items-center text-center mt-2 mb-2 gap-4">
      <div className="max-w-2xl">
        <h2 className="text-3xl md:text-5xl font-display font-bold mb-2">Is that payment request lying to you?</h2>
        <p className="text-base md:text-lg text-text-muted">Paste a message, link, or QR — VeriFi investigates the evidence, not the vibes.</p>
      </div>

      <div className="glass-panel w-full max-w-3xl p-1 flex flex-col gap-2">
        <div className="flex items-center gap-2 border-b border-border-glass p-1">
          <button onClick={()=>setTab('text')} className={clsx("flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors", tab==='text' ? "bg-black/10 dark:bg-white/10 text-text-primary":"text-text-muted hover:text-text-primary")}><FileText size={16}/> Text</button>
          <button onClick={()=>setTab('url')} className={clsx("flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors", tab==='url' ? "bg-black/10 dark:bg-white/10 text-text-primary":"text-text-muted hover:text-text-primary")}><LinkIcon size={16}/> URL</button>
          <button onClick={()=>setTab('qr')} className={clsx("flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors", tab==='qr' ? "bg-black/10 dark:bg-white/10 text-text-primary":"text-text-muted hover:text-text-primary")}><ImageIcon size={16}/> QR</button>
        </div>
        
        <div className="p-3 min-h-[120px] flex items-center justify-center">
          {tab === 'text' && <textarea className="w-full h-24 bg-transparent border-none outline-none resize-none text-lg text-text-primary placeholder:text-text-muted/50" placeholder="Paste the suspicious SMS, WhatsApp message, or UPI request here..." value={input} onChange={e=>setInput(e.target.value)} />}
          {tab === 'url' && <input type="url" className="w-full bg-transparent border-b border-border-glass pb-2 outline-none text-xl text-center" placeholder="https://" value={input} onChange={e=>setInput(e.target.value)} />}
          {tab === 'qr' && (
            <div 
              onDragOver={(e) => e.preventDefault()} 
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className="w-full h-24 border-2 border-dashed border-border-glass rounded-xl flex items-center justify-center text-text-muted hover:border-blue-500/50 hover:text-blue-500 transition-colors cursor-pointer"
            >
              <input type="file" ref={fileInputRef} className="hidden" accept="image/*" onChange={handleFileChange} />
              {qrFile ? qrFile.name : "Drop QR image here or click to browse"}
            </div>
          )}
        </div>

        <div className="p-2">
          <button onClick={() => onRun(tab, tab === 'qr' ? qrFile : input)} className="w-full py-3 rounded-xl font-display font-bold text-lg text-white bg-[var(--accent)] shadow-[0_0_20px_rgba(99,102,241,0.4)] hover:shadow-[0_0_30px_rgba(6,182,212,0.6)] hover:scale-[0.99] transition-all duration-300">Run Deep Investigation</button>
        </div>
      </div>
    </div>
  );
}
