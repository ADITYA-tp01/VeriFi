import { Copy, Download, CheckCircle2 } from 'lucide-react';
import { useState } from 'react';

export default function PlaybookDeck({ incidentData }: { incidentData?: any }) {
  const [copied, setCopied] = useState(false);
  const [copiedStep, setCopiedStep] = useState<number | null>(null);

  const bank = incidentData?.bank || "[BANK]";
  const txn = incidentData?.txn || "[TXN_ID]";
  const amount = incidentData?.amount || "[AMOUNT]";
  const time = incidentData?.time || "[TIME]";
  
  const steps = [
    { title: "Call 1930 RIGHT NOW", desc: "Government cyber-fraud helpline, 24x7. Tell them your transaction ID and bank. Ask them to flag it for recall — the first hours matter most.", template: `I am reporting a cyber fraud. Transaction ID: ${txn}. Amount: ${amount}. Bank: ${bank}.` },
    { title: "File a complaint at cybercrime.gov.in", desc: "Log in → Report Suspicious Activity → Financial Fraud. Use the same details and upload any screenshots.", template: `Complaint filed against UPI ID/Txn: ${txn}. Time of incident: ${time}.` },
    { title: "Call your bank's fraud desk", desc: "Request a chargeback / recall for the transaction. Banks must respond promptly.", template: `To Nodal Officer: Requesting immediate chargeback for fraud txn ${txn}.` },
    { title: "Secure your account NOW", desc: "Change your UPI PIN and net-banking password from the official app.", template: "" },
  ];

  const handleCopy = (text: string, index?: number) => {
    navigator.clipboard.writeText(text);
    if (index !== undefined) {
      setCopiedStep(index);
      setTimeout(() => setCopiedStep(null), 2000);
    } else {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="glass-panel p-0 h-full overflow-hidden flex flex-col border-emerald-500/20 shadow-[0_0_40px_rgba(16,185,129,0.05)]">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between bg-emerald-500/5 p-6 border-b border-border-glass gap-4">
        <div className="flex flex-col gap-1">
          <h3 className="text-xl font-display font-medium text-emerald-700 dark:text-emerald-400">Your Complaint Kit</h3>
          <span className="text-[16px] text-text-muted">Follow these exact steps to maximize recovery chances.</span>
        </div>
        <button 
          onClick={() => handleCopy(steps.map(s => s.template).filter(Boolean).join('\n\n'))}
          className="flex items-center justify-center gap-2 px-6 py-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition-all w-full sm:w-auto text-lg h-14"
        >
          {copied ? <CheckCircle2 size={22}/> : <Copy size={22}/>}
          {copied ? "Copied All" : "Copy Full Complaint"}
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6 bg-black/5 dark:bg-transparent">
        {steps.map((s, i) => (
          <div key={i} className="glass-panel p-5 flex flex-col gap-4 border-emerald-500/10 bg-white dark:bg-bg-panel">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-500 flex items-center justify-center font-mono font-bold shrink-0 text-lg">{i+1}</div>
              <div className="flex flex-col gap-2 flex-1 mt-1">
                <h4 className="font-bold text-[18px]">{s.title}</h4>
                <p className="text-[16px] text-text-muted leading-relaxed">{s.desc}</p>
                {s.template && (
                  <div className="mt-3 bg-emerald-50 dark:bg-black/40 p-3 rounded-xl border border-emerald-500/20 dark:border-border-glass relative group flex items-center justify-between gap-4 cursor-pointer hover:bg-emerald-100 dark:hover:bg-black/60 transition-colors">
                    <p className="font-mono text-[14px] text-emerald-700 dark:text-emerald-400">{s.template}</p>
                    <button onClick={() => handleCopy(s.template, i)} className="text-emerald-600/50 hover:text-emerald-600 transition-colors shrink-0 bg-emerald-500/10 p-2 rounded-lg">
                      {copiedStep === i ? <CheckCircle2 size={18}/> : <Copy size={18}/>}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
