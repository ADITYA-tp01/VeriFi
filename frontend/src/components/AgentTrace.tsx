import { CheckCircle2, Cpu } from 'lucide-react';

export default function AgentTrace({ docked, traceLog }: any) {
  const defaultSteps = [
    { text: "Input routed → ANALYZE mode", done: true },
    { text: "Planner deciding: escalate to deep scan…", done: !docked },
  ];

  const steps = traceLog ? traceLog.map((t: any) => ({
    text: `${t.node} → ${t.decision}`,
    done: true
  })) : defaultSteps;

  return (
    <div className={`flex flex-col items-center justify-center ${docked ? 'h-full' : 'py-20'}`}>
      <div className={`glass-panel p-6 sm:p-8 w-full ${docked ? 'h-full flex flex-col justify-start' : 'max-w-[1200px]'}`}>
        <h3 className="text-xl font-display font-medium mb-6 flex items-center gap-3"><Cpu className="text-blue-500" /> Live Agent Trace</h3>
        <div className="flex flex-col gap-4 relative pl-4 border-l border-border-glass">
          {steps.map((step, i) => {
            if (docked && !step.done) return null; // hide loading in docked
            return (
              <div key={i} className={`flex items-start gap-4 transition-all duration-500 ${step.done ? 'opacity-70' : 'opacity-100 scale-[1.02]'}`}>
                <div className="relative -ml-[25px] mt-1 bg-bg-abyss">
                  {step.done ? <CheckCircle2 size={18} className="text-emerald-500" /> : <span className="flex w-[18px] h-[18px] rounded-full border-2 border-blue-500/50 items-center justify-center"><span className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></span></span>}
                </div>
                <span className="font-mono text-sm tracking-tight">{step.text}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  );
}
