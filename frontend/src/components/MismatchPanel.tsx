import { AlertTriangle, CheckCircle2, ShieldCheck, ArrowRight, Layers } from 'lucide-react';

export default function MismatchPanel({ intent, mechanism, mismatch }: any) {
  return (
    <div className="flex flex-col gap-6">
      {/* Evidence Vector Comparison Card */}
      <div className="glass-panel p-6 border-white/10 flex flex-col gap-4">
        <div className="flex items-center justify-between pb-3 border-b border-border-glass">
          <div className="flex items-center gap-2">
            <Layers size={18} className="text-blue-400" />
            <h3 className="font-display font-medium text-lg text-text-primary">Intent vs Mechanism Verification</h3>
          </div>
          <span className={`text-xs font-mono font-bold px-2.5 py-1 rounded-full uppercase tracking-wider ${
            mismatch 
              ? 'bg-risk-critical/15 text-risk-critical border border-risk-critical/30' 
              : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
          }`}>
            {mismatch ? 'Intent Mismatch' : 'Mechanisms Aligned'}
          </span>
        </div>

        <div className="flex flex-col md:flex-row items-stretch gap-4 pt-2">
          {/* Claimed Intent */}
          <div className="flex-1 glass-panel px-5 py-5 border-blue-500/20 bg-blue-500/5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold tracking-widest uppercase text-blue-400 font-mono">Narrative Intent (Claim)</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 font-mono">Text Agent</span>
              </div>
              <div className="font-mono text-xl font-semibold text-text-primary">{intent || 'Unknown'}</div>
            </div>
            <p className="text-xs text-text-muted mt-3 pt-2 border-t border-blue-500/10">
              Extracted psychological framing: What the sender promises you will happen.
            </p>
          </div>
          
          {/* Middle Comparison Node */}
          <div className="w-full md:w-[100px] flex flex-row md:flex-col items-center justify-center shrink-0 my-2 md:my-0 relative">
            <div className="w-full h-[2px] md:w-[2px] md:h-full bg-border-glass absolute top-1/2 md:top-0 left-0 md:left-1/2 -translate-y-1/2 md:-translate-y-0 md:-translate-x-1/2 z-0"></div>
            <div className="z-10 bg-bg-abyss p-2 rounded-xl border border-border-glass">
              {mismatch ? (
                <div className="w-10 h-10 rounded-full bg-risk-critical/10 border-2 border-risk-critical flex items-center justify-center text-risk-critical shadow-[0_0_20px_rgba(239,68,68,0.4)]">
                  <AlertTriangle size={20} />
                </div>
              ) : (
                <div className="w-10 h-10 rounded-full bg-emerald-500/10 border-2 border-emerald-500 flex items-center justify-center text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)]">
                  <ShieldCheck size={20} />
                </div>
              )}
            </div>
          </div>
          
          {/* Executed Payload */}
          <div className={`flex-1 glass-panel px-5 py-5 flex flex-col justify-between ${
            mismatch ? 'border-risk-critical/30 bg-risk-critical/10' : 'border-emerald-500/20 bg-emerald-500/5'
          }`}>
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className={`text-xs font-bold tracking-widest uppercase font-mono ${
                  mismatch ? 'text-risk-critical' : 'text-emerald-400'
                }`}>
                  Execution Payload (Reality)
                </span>
                <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${
                  mismatch ? 'bg-risk-critical/10 text-risk-critical' : 'bg-emerald-500/10 text-emerald-300'
                }`}>
                  Deterministic QR/UPI
                </span>
              </div>
              <div className="font-mono text-xl font-semibold text-text-primary">{mechanism || 'None / Not Applicable'}</div>
            </div>
            <p className="text-xs text-text-muted mt-3 pt-2 border-t border-border-glass">
              Decoded payment directive: What the banking app actually executes when scanned.
            </p>
          </div>
        </div>
      </div>

      {/* Concrete finding summary */}
      {mismatch ? (
        <div className="glass-panel border-risk-critical/30 bg-risk-critical/10 p-5 flex items-start gap-4">
          <div className="p-2 rounded-lg bg-risk-critical/20 text-risk-critical shrink-0">
            <AlertTriangle size={22} />
          </div>
          <div>
            <h4 className="font-bold text-red-100 text-base">CRITICAL INTENT DIVERGENCE DETECTED</h4>
            <p className="text-sm text-red-200/90 mt-1 leading-relaxed">
              The communication asserts that you are <strong>receiving funds</strong>, but the deterministic payload triggers an <strong>account debit</strong>. In India UPI protocols, entering your PIN always authorizes money going out.
            </p>
          </div>
        </div>
      ) : (
        <div className="glass-panel border-emerald-500/30 bg-emerald-500/10 p-5 flex items-start gap-4">
          <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400 shrink-0">
            <CheckCircle2 size={22} />
          </div>
          <div>
            <h4 className="font-bold text-emerald-100 text-base">NO DECEPTIVE MISMATCH</h4>
            <p className="text-sm text-emerald-200/90 mt-1 leading-relaxed">
              The stated transaction purpose matches the underlying payment action without contradictory debit/credit deception.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
