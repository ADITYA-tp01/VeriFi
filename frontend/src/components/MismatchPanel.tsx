import { AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function MismatchPanel({ intent, mechanism, mismatch }: any) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col md:flex-row items-stretch">
        <div className="flex-1 glass-panel px-5 py-6 border-blue-500/20 bg-blue-500/5">
          <h3 className="text-sm font-bold tracking-wider uppercase text-blue-400 mb-4">WHAT THE MESSAGE CLAIMS</h3>
          <div className="font-mono text-xl">{intent}</div>
          <p className="text-sm text-text-muted mt-2">Narrative intent extracted from text.</p>
        </div>
        
        <div className="w-full md:w-[120px] flex flex-row md:flex-col items-center justify-center shrink-0 my-4 md:my-0 relative">
          <div className="w-full h-[2px] md:w-[2px] md:h-full bg-border-glass absolute top-1/2 md:top-0 left-0 md:left-1/2 -translate-y-1/2 md:-translate-y-0 md:-translate-x-1/2 z-0"></div>
          {mismatch && (
            <div className="flex flex-row md:flex-col items-center z-10 bg-bg-abyss p-2 rounded-xl">
              <div className="w-10 h-10 md:w-12 md:h-12 rounded-full bg-bg-abyss border-2 border-risk-critical flex items-center justify-center text-risk-critical shadow-[0_0_20px_rgba(239,68,68,0.5)]">
                <AlertTriangle size={20} className="md:w-6 md:h-6" />
              </div>
              <span className="bg-risk-critical text-white font-bold text-[10px] px-2 py-1 rounded-full ml-3 md:ml-0 md:mt-2 tracking-wider text-center md:block flex items-center">
                <span className="md:hidden">MISMATCH</span>
                <span className="hidden md:inline">MISMATCH<br/>DETECTED</span>
              </span>
            </div>
          )}
        </div>
        
        <div className={`flex-1 glass-panel px-5 py-6 ${mismatch ? 'border-risk-critical/30 bg-risk-critical/10' : 'border-risk-clean/30 bg-risk-clean/10'}`}>
          <h3 className={`text-sm font-bold tracking-wider uppercase ${mismatch ? 'text-risk-critical' : 'text-risk-clean'} mb-4`}>WHAT THE MECHANISM EXECUTES</h3>
          <div className="font-mono text-xl">{mechanism}</div>
          <p className="text-sm text-text-muted mt-2">Deterministic payload decoded from QR.</p>
        </div>
      </div>

      {mismatch && (
        <div className="glass-panel border-red-500/30 bg-red-500/10 p-4 flex items-start gap-4">
          <AlertTriangle className="text-red-500 shrink-0" />
          <div>
            <h4 className="font-bold text-red-100">KEY MISMATCH FINDING</h4>
            <p className="text-sm text-red-200/80 mt-1">The message claims you will receive money, but the QR actually debits your account. This is direct evidence of deception.</p>
          </div>
        </div>
      )}
    </div>
  );
}
