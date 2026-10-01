import { useState } from 'react';
import { Send } from 'lucide-react';
import logoUrl from '../assets/logo.png';

export default function IncidentChat({ onComplete }: { onComplete?: (data: any) => void }) {
  const [messages, setMessages] = useState([
    { role: 'agent', text: "Take a breath — you're doing the right thing. Answer a few quick questions and I'll prepare your official complaint step by step. First, what bank was the money sent from?" }
  ]);
  const [input, setInput] = useState('');

  const send = (text: string = input) => {
    if(!text.trim()) return;
    
    const newMessages = [...messages, { role: 'user', text }];
    setMessages(newMessages);
    setInput('');

    // Simulate Agent response
    setTimeout(() => {
      let agentReply = "";
      const hasOther = newMessages[1]?.text === 'Other';
      const offset = hasOther ? 2 : 0;

      if (newMessages.length === 2 && hasOther) {
        agentReply = "Could you please specify the name of the bank and the payment mode you used?";
      } else if (newMessages.length === 2 + offset) {
        agentReply = "Got it. What was the exact Transaction ID or UPI reference number? (reply 'skip' if you don't have it)";
      } else if (newMessages.length === 4 + offset) {
        agentReply = "Understood. What was the exact amount lost?";
      } else if (newMessages.length === 6 + offset) {
        agentReply = "Almost done. Approximately what date and time did this happen?";
      } else if (newMessages.length === 8 + offset) {
        agentReply = "Thank you. I have generated your personalized Complaint Kit on the right. Please follow those steps immediately to maximize your chances of recovery.";
        if (onComplete) {
          onComplete({
            bank: hasOther ? newMessages[3].text : newMessages[1].text,
            txn: newMessages[3 + offset].text,
            amount: newMessages[5 + offset].text,
            time: newMessages[7 + offset].text
          });
        }
      }
      
      if (agentReply) {
        setMessages(prev => [...prev, { role: 'agent', text: agentReply }]);
      }
    }, 1000);
  };

  return (
    <div className="glass-panel flex flex-col h-full overflow-hidden border-indigo-500/20 shadow-[0_0_40px_rgba(99,102,241,0.05)]">
      <div className="bg-indigo-500/5 p-5 border-b border-border-glass flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img src={logoUrl} alt="VeriFi Logo" className="w-6 h-6 object-contain" />
          <span className="font-display font-semibold text-lg text-indigo-900 dark:text-indigo-100">Incident Interview</span>
        </div>
        <span className="text-xs font-mono font-bold text-indigo-600 dark:text-indigo-400">Step 1 of 4</span>
      </div>
      <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
        {messages.map((m, i) => (
          <div key={i} className={`flex items-start gap-4 max-w-[85%] ${m.role === 'user' ? 'self-end flex-row-reverse' : ''}`}>
            {m.role === 'agent' && <div className="w-10 h-10 rounded-full bg-indigo-500/10 flex items-center justify-center shrink-0 border border-indigo-500/20"><img src={logoUrl} alt="Agent" className="w-5 h-5 object-contain" /></div>}
            <div className={`p-4 rounded-2xl text-[18px] leading-relaxed ${m.role === 'user' ? 'bg-indigo-600 text-white' : 'glass-panel border-indigo-500/10 shadow-none bg-white dark:bg-black/20'}`}>
              {m.text}
            </div>
          </div>
        ))}
        {messages.length === 1 && (
          <div className="flex flex-wrap gap-2 ml-14">
            {['HDFC', 'SBI', 'ICICI', 'Axis', 'Other'].map(b => (
              <button key={b} onClick={() => send(b)} className="px-5 py-2 rounded-full border border-indigo-500/30 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-500/10 transition-colors text-lg font-medium">{b}</button>
            ))}
          </div>
        )}
        {(() => {
          const hasOther = messages[1]?.text === 'Other';
          const offset = hasOther ? 2 : 0;
          if (messages.length === 3 + offset) {
            return (
              <div className="flex flex-wrap gap-2 ml-14">
                <button onClick={() => send('skip')} className="px-5 py-2 rounded-full border border-indigo-500/30 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-500/10 transition-colors text-lg font-medium">I don't have it / Skip</button>
              </div>
            );
          }
          return null;
        })()}
      </div>
      <div className="p-4 border-t border-border-glass flex gap-3 bg-black/5 dark:bg-transparent">
        <input 
          type="text" 
          value={input} 
          onChange={e=>setInput(e.target.value)} 
          onKeyDown={e => e.key==='Enter' && send()}
          className="flex-1 bg-white/50 dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-xl px-5 py-3 outline-none focus:border-indigo-500/50 transition-colors text-lg" 
          placeholder="Type your answer..."
        />
        <button onClick={() => send()} className="w-14 h-14 rounded-xl bg-indigo-600 hover:bg-indigo-500 flex items-center justify-center text-white transition-colors shrink-0"><Send size={22}/></button>
      </div>
    </div>
  );
}
