import { Shield, Sun, Moon } from 'lucide-react';
import { clsx } from 'clsx';
import logoUrl from '../assets/logo.png';

export default function Header({ mode, setMode, theme, setTheme }: any) {
  return (
    <header className="fixed top-0 left-0 w-full z-50 glass-panel border-t-0 border-x-0 rounded-none px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <button 
          onClick={() => window.location.href = '/'} 
          className="relative group flex items-center justify-center w-10 h-10 rounded-full overflow-hidden border border-border-glass bg-white/5 hover:border-blue-500/50 transition-colors"
          title="Go to Homepage"
        >
          <img src={logoUrl} alt="VeriFi Logo" className="w-12 h-12 object-cover scale-[1.3] group-hover:scale-[1.5] group-hover:rotate-12 transition-transform duration-500" />
        </button>
        <div className="flex flex-col">
          <h1 className="font-display font-bold text-xl tracking-wide bg-accent text-transparent bg-clip-text">VeriFi</h1>
        </div>
        <span className="ml-4 px-2 py-1 text-[10px] font-mono border border-blue-500/30 text-blue-400 rounded-full bg-blue-500/10 hidden md:inline-block">BHARAT AGENTIC 2026</span>
      </div>
      
      <div className="flex items-center gap-2 bg-black/40 dark:bg-white/10 p-1 rounded-full border border-border-glass">
        <button 
          onClick={() => setMode('analyze')}
          className={clsx("px-4 py-1.5 rounded-full text-sm font-medium transition-all", mode === 'analyze' ? "bg-white shadow-lg text-black dark:bg-white/10 dark:text-white" : "text-text-muted hover:text-text-primary")}
        >
          Analyze Threat
        </button>
        <button 
          onClick={() => setMode('incident')}
          className={clsx("px-4 py-1.5 rounded-full text-sm font-medium transition-all", mode === 'incident' ? "bg-white shadow-lg text-black dark:bg-white/10 dark:text-white" : "text-text-muted hover:text-text-primary")}
        >
          Incident Response
        </button>
      </div>

      <div className="flex items-center gap-6">
        <button 
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-2 rounded-full border border-border-glass bg-black/5 dark:bg-black/40 hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
        >
          {theme === 'dark' ? <Sun size={18} className="text-text-muted hover:text-text-primary" /> : <Moon size={18} className="text-text-muted hover:text-text-primary" />}
        </button>
        
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-risk-clean shadow-[0_0_8px_#10B981] animate-pulse"></span>
          <span className="text-xs font-mono text-text-muted hidden sm:inline-block">Engine Active</span>
        </div>
      </div>
    </header>
  );
}
