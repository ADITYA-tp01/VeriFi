import { Copy, Download, CheckCircle2, PhoneCall, CheckSquare, Square, FileText } from 'lucide-react';
import { useState } from 'react';

export default function PlaybookDeck({ incidentData }: { incidentData?: any }) {
  const [copied, setCopied] = useState(false);
  const [copiedStep, setCopiedStep] = useState<number | null>(null);
  const [checkedSteps, setCheckedSteps] = useState<Record<number, boolean>>({});

  const bank = incidentData?.bank || "[BANK_NAME]";
  const txn = incidentData?.txn || "[TRANSACTION_ID]";
  const amount = incidentData?.amount || "[AMOUNT_INR]";
  const time = incidentData?.time || "[TIMESTAMP]";
  
  const steps = [
    { 
      title: "Call 1930 Helpline IMMEDIATELY", 
      desc: "National Cyber Fraud Reporting helpline (24x7). State your Transaction ID and bank. Demand an immediate recall/freeze before funds leave the mule account chain.", 
      template: `URGENT: I am reporting an unauthorized cyber fraud transaction. Bank: ${bank}, Txn ID: ${txn}, Amount Lost: ${amount}, Incident Time: ${time}. Please flag for immediate recall.`,
      action: { type: 'phone', label: 'Call 1930 Now', link: 'tel:1930' }
    },
    { 
      title: "Lodge FIR / Complaint on cybercrime.gov.in", 
      desc: "Navigate to 'Report Financial Fraud'. Input exact transaction details and attach relevant screenshots/chat logs to generate an official acknowledgement slip.", 
      template: `Formal Incident Complaint: Fraudulent payment executed via UPI / Netbanking. Disputed Amount: ${amount}. Destination Bank / Details: ${bank}. Reference: ${txn}. Incident Timestamp: ${time}.`,
      action: { type: 'web', label: 'Open Cybercrime Portal', link: 'https://cybercrime.gov.in' }
    },
    { 
      title: "Notify Bank Fraud Desk & Nodal Officer", 
      desc: "Submit an official dispute under RBI Cyber Fraud Guidelines for chargeback initiation and transaction repudiation.", 
      template: `To The Principal Nodal Officer, ${bank}:\nSub: Immediate chargeback request for unauthorized transaction ${txn} of ${amount}.\nDate/Time: ${time}.\nI dispute this transaction as deceptive fraud and request account credit freeze under RBI guidelines.`,
      action: null
    },
    { 
      title: "Secure Digital Credentials & App Access", 
      desc: "Immediately reset your UPI PIN and Net Banking passwords through your bank's verified mobile app. Revoke active device sessions.", 
      template: "",
      action: null
    },
  ];

  const toggleCheck = (index: number) => {
    setCheckedSteps(prev => ({ ...prev, [index]: !prev[index] }));
  };

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

  const downloadComplaintFile = () => {
    const fullText = `=====================================================
VERIFI OFFICIAL INCIDENT COMPLAINT DOSSIER
Generated via VeriFi Bharat Financial Safety Engine
=====================================================
Bank Account Involved : ${bank}
Transaction Reference : ${txn}
Disputed Amount       : ${amount}
Approximate Timestamp : ${time}
=====================================================

1. CITIZEN STATEMENT FOR 1930 HELPLINE:
${steps[0].template}

2. CYBERCRIME.GOV.IN PORTAL SUBMISSION TEXT:
${steps[1].template}

3. BANK FORMAL CHARGEBACK LETTER:
${steps[2].template}

=====================================================
INSTRUCTIONS:
1. Dial 1930 immediately to freeze beneficiary accounts.
2. Submit Section 2 to cybercrime.gov.in and record acknowledgment number.
3. Deliver Section 3 via registered email to your bank's Nodal Officer.
=====================================================`;

    const blob = new Blob([fullText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `VeriFi_Complaint_${txn.replace(/[^a-zA-Z0-9]/g, '_')}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const completedCount = Object.values(checkedSteps).filter(Boolean).length;

  return (
    <div className="glass-panel p-0 h-full overflow-hidden flex flex-col border-emerald-500/20 shadow-[0_0_40px_rgba(16,185,129,0.05)]">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between bg-emerald-500/5 p-5 sm:p-6 border-b border-border-glass gap-4">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <h3 className="text-xl font-display font-medium text-emerald-700 dark:text-emerald-400">
              Official Incident Recovery Kit
            </h3>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {completedCount} of 4 Complete
            </span>
          </div>
          <span className="text-sm text-text-muted">Structured action items and pre-drafted complaint templates.</span>
        </div>
        
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button 
            type="button"
            onClick={downloadComplaintFile}
            className="flex items-center justify-center gap-1.5 px-3.5 py-2.5 rounded-xl border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 text-sm font-medium transition-colors flex-1 sm:flex-initial"
            title="Download formatted complaint draft"
          >
            <Download size={16} />
            <span>Download Dossier</span>
          </button>
          
          <button 
            type="button"
            onClick={() => handleCopy(steps.map(s => s.template).filter(Boolean).join('\n\n'))}
            className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition-all text-sm shadow-md flex-1 sm:flex-initial"
          >
            {copied ? <CheckCircle2 size={16}/> : <Copy size={16}/>}
            <span>{copied ? "Copied All" : "Copy Dossier"}</span>
          </button>
        </div>
      </div>
      
      {/* Action Plan Checklist Deck */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 flex flex-col gap-4 bg-black/5 dark:bg-transparent">
        {steps.map((s, i) => {
          const isDone = !!checkedSteps[i];

          return (
            <div 
              key={i} 
              className={`glass-panel p-4 sm:p-5 flex flex-col gap-3 transition-all border ${
                isDone 
                  ? 'border-emerald-500/30 bg-emerald-500/5 opacity-80' 
                  : 'border-white/10 bg-white dark:bg-bg-panel hover:border-emerald-500/20'
              }`}
            >
              <div className="flex items-start gap-3.5">
                <button 
                  type="button"
                  onClick={() => toggleCheck(i)} 
                  className="mt-0.5 text-text-muted hover:text-emerald-400 transition-colors shrink-0"
                  title={isDone ? "Mark incomplete" : "Mark step completed"}
                >
                  {isDone ? (
                    <CheckSquare size={22} className="text-emerald-400" />
                  ) : (
                    <Square size={22} className="opacity-40" />
                  )}
                </button>

                <div className="flex flex-col gap-1.5 flex-1">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h4 className={`font-bold text-base ${isDone ? 'line-through text-text-muted' : 'text-text-primary'}`}>
                      {i + 1}. {s.title}
                    </h4>

                    {s.action && (
                      <a 
                        href={s.action.link} 
                        target={s.action.type === 'web' ? '_blank' : '_self'}
                        rel="noreferrer"
                        className="flex items-center gap-1 text-xs px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/20 font-mono transition-colors"
                      >
                        {s.action.type === 'phone' && <PhoneCall size={12} />}
                        <span>{s.action.label}</span>
                      </a>
                    )}
                  </div>

                  <p className="text-xs sm:text-sm text-text-muted leading-relaxed">{s.desc}</p>

                  {s.template && (
                    <div 
                      onClick={() => handleCopy(s.template, i)}
                      className="mt-2 bg-emerald-50 dark:bg-black/40 p-3 rounded-xl border border-emerald-500/20 dark:border-border-glass flex items-center justify-between gap-3 cursor-pointer hover:bg-emerald-100 dark:hover:bg-black/60 transition-colors group"
                      title="Click to copy template"
                    >
                      <p className="font-mono text-xs sm:text-sm text-emerald-800 dark:text-emerald-400 select-all overflow-hidden text-ellipsis">
                        {s.template}
                      </p>
                      <span className="text-emerald-600/60 group-hover:text-emerald-500 transition-colors shrink-0 p-1.5 rounded-lg bg-emerald-500/10">
                        {copiedStep === i ? <CheckCircle2 size={16}/> : <Copy size={16}/>}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
