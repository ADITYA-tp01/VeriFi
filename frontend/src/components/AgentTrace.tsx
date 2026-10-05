import { CheckCircle2, Cpu, Loader2, ArrowRight } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function AgentTrace({ docked, traceLog }: any) {
  const [activeStepIndex, setActiveStepIndex] = useState(0);

  const fullPipelineSteps = [
    { name: "Gateway Classifier", text: "Routing input payload → Multi-Agent Investigation Loop", time: "12ms" },
    { name: "Visual Decoder", text: "Computer Vision OCR: scanning for UPI intent, merchant VPA, amount parameters", time: "48ms" },
    { name: "Network Intelligence", text: "WHOIS & DNS Threat Intel: analyzing registrar age, domain entropy, SSL trust", time: "85ms" },
    { name: "Narrative Analyzer", text: "NLP Reasoning: extracting urgency markers, deceptive framing, and payment purpose", time: "120ms" },
    { name: "Deterministic Verifier", text: "Cross-Vector Check: verifying claimed credit vs actual debit execution payload", time: "160ms" },
    { name: "Risk Synthesizer", text: "Compiling multi-layered Bayesian score vector and mitigation playbook", time: "195ms" },
  ];

  useEffect(() => {
    if (!docked) {
      const interval = setInterval(() => {
        setActiveStepIndex(prev => (prev < fullPipelineSteps.length - 1 ? prev + 1 : prev));
      }, 700);
      return () => clearInterval(interval);
    }
  }, [docked]);

  const steps = traceLog ? traceLog.map((t: any) => ({
    name: t.node || 'Agent Node',
    text: `${t.node} → ${t.decision}`,
    done: true,
    time: t.time || 'verified'
  })) : fullPipelineSteps.map((s, idx) => ({
    ...s,
    done: docked ? true : idx < activeStepIndex,
    inProgress: !docked && idx === activeStepIndex
  }));

  return (
    <div className={`flex flex-col items-center justify-center ${docked ? 'h-full' : 'py-12'}`}>
      <div className={`glass-panel p-6 sm:p-8 w-full ${docked ? 'h-full flex flex-col justify-start' : 'max-w-[850px] shadow-2xl border-blue-500/20'}`}>
        <div className="flex items-center justify-between mb-6 pb-3 border-b border-border-glass">
          <h3 className="text-xl font-display font-medium flex items-center gap-3">
            <Cpu className="text-blue-500" /> 
            <span>{docked ? "Execution Trace Audit" : "Multi-Agent Engine Orchestrating..."}</span>
          </h3>
          {!docked && (
            <span className="flex items-center gap-2 text-xs font-mono text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full border border-blue-500/20">
              <Loader2 size={13} className="animate-spin" /> Deep Pipeline Active
            </span>
          )}
        </div>

        <div className="flex flex-col gap-4 relative pl-4 border-l border-border-glass">
          {steps.map((step: any, i: number) => {
            if (docked && !step.done) return null;
            const isCurrent = step.inProgress;

            return (
              <div 
                key={i} 
                className={`flex items-start gap-4 transition-all duration-300 ${
                  step.done ? 'opacity-90' : isCurrent ? 'opacity-100 scale-[1.01]' : 'opacity-40'
                }`}
              >
                <div className="relative -ml-[25px] mt-1 bg-bg-abyss shrink-0">
                  {step.done ? (
                    <CheckCircle2 size={18} className="text-emerald-500" />
                  ) : isCurrent ? (
                    <span className="flex w-[18px] h-[18px] rounded-full border-2 border-blue-500 items-center justify-center bg-blue-500/20">
                      <span className="w-2 h-2 bg-blue-400 rounded-full animate-ping" />
                    </span>
                  ) : (
                    <span className="w-[18px] h-[18px] rounded-full border border-white/20 block" />
                  )}
                </div>

                <div className="flex flex-col gap-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-text-muted uppercase tracking-wider">{step.name}</span>
                    {step.time && <span className="text-[10px] font-mono text-text-muted/60">{step.time}</span>}
                  </div>
                  <span className="font-mono text-sm tracking-tight text-text-primary">{step.text}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
