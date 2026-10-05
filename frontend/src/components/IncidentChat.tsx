import { useState, useRef, useEffect } from 'react';
import { Send, RotateCcw, ShieldAlert, CheckCircle } from 'lucide-react';
import logoUrl from '../assets/logo.png';

export default function IncidentChat({ onComplete }: { onComplete?: (data: any) => void }) {
  const initialGreeting = "Take a breath — you're doing the right thing. Answer a few quick questions and I'll prepare your official complaint step by step. First, what bank was the money sent from?";
  
  const [messages, setMessages] = useState<{ role: 'agent' | 'user'; text: string }[]>([
    { role: 'agent', text: initialGreeting }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const resetInterview = () => {
    setMessages([{ role: 'agent', text: initialGreeting }]);
    setInput('');
    setIsTyping(false);
    if (onComplete) onComplete(null);
  };

  const calculateStep = () => {
    const userMsgCount = messages.filter(m => m.role === 'user').length;
    return Math.min(4, Math.max(1, userMsgCount + 1));
  };

  const currentStep = calculateStep();

  const send = (text: string = input) => {
    if (!text.trim() || isTyping) return;
    
    const newMessages = [...messages, { role: 'user' as const, text: text.trim() }];
    setMessages(newMessages);
    setInput('');
    setIsTyping(true);

    // Dynamic interview progression
    setTimeout(() => {
      let agentReply = "";
      const hasOther = newMessages[1]?.text === 'Other';
      const offset = hasOther ? 2 : 0;

      if (newMessages.length === 2 && hasOther) {
        agentReply = "Could you please specify the name of the bank and the payment mode you used?";
      } else if (newMessages.length === 2 + offset) {
        agentReply = "Got it. What was the exact Transaction ID or UPI reference number? (reply 'skip' if you don't have it handy)";
      } else if (newMessages.length === 4 + offset) {
        agentReply = "Understood. What was the exact amount lost in INR (₹)?";
      } else if (newMessages.length === 6 + offset) {
        agentReply = "Almost done. Approximately when did this incident happen?";
      } else if (newMessages.length === 8 + offset) {
        agentReply = "Thank you. I have synthesized your details and generated your official Emergency Complaint Kit on the right. Act on these steps immediately!";
        if (onComplete) {
          onComplete({
            bank: hasOther ? newMessages[3]?.text : newMessages[1]?.text,
            txn: newMessages[3 + offset]?.text || "PENDING_VERIFICATION",
            amount: newMessages[5 + offset]?.text || "UNSPECIFIED",
            time: newMessages[7 + offset]?.text || "RECENT"
          });
        }
      }
      
      setIsTyping(false);
      if (agentReply) {
        setMessages(prev => [...prev, { role: 'agent', text: agentReply }]);
      }
    }, 800);
  };

  const hasOther = messages[1]?.text === 'Other';
  const offset = hasOther ? 2 : 0;

  return (
    <div className="glass-panel flex flex-col h-full overflow-hidden border-indigo-500/20 shadow-[0_0_40px_rgba(99,102,241,0.05)]">
      {/* Incident Header & Step Progress Bar */}
      <div className="bg-indigo-500/5 p-4 sm:p-5 border-b border-border-glass flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src={logoUrl} alt="VeriFi Logo" className="w-6 h-6 object-contain" />
            <div className="flex flex-col">
              <span className="font-display font-semibold text-base sm:text-lg text-indigo-900 dark:text-indigo-100 flex items-center gap-2">
                Emergency Incident Triage
              </span>
              <span className="text-[11px] text-text-muted">Direct intake for 1930 & cybercrime filing</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={resetInterview} 
              className="p-1.5 rounded-lg border border-border-glass hover:bg-white/10 text-text-muted hover:text-text-primary transition-colors text-xs flex items-center gap-1"
              title="Reset interview"
            >
              <RotateCcw size={13} />
              <span className="hidden sm:inline">Restart</span>
            </button>
            <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Step {currentStep} of 4
            </span>
          </div>
        </div>

        {/* Linear progress bar */}
        <div className="w-full bg-black/10 dark:bg-white/5 h-1 rounded-full overflow-hidden">
          <div 
            className="bg-indigo-500 h-full rounded-full transition-all duration-500" 
            style={{ width: `${(currentStep / 4) * 100}%` }}
          />
        </div>
      </div>

      {/* Messages View */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 flex flex-col gap-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex items-start gap-3 max-w-[88%] ${m.role === 'user' ? 'self-end flex-row-reverse' : ''}`}>
            {m.role === 'agent' && (
              <div className="w-8 h-8 rounded-full bg-indigo-500/10 flex items-center justify-center shrink-0 border border-indigo-500/20 mt-1">
                <img src={logoUrl} alt="Agent" className="w-4 h-4 object-contain" />
              </div>
            )}
            <div className={`p-3.5 sm:p-4 rounded-2xl text-[15px] sm:text-[16px] leading-relaxed ${
              m.role === 'user' 
                ? 'bg-indigo-600 text-white rounded-br-none shadow-md' 
                : 'glass-panel border-indigo-500/10 shadow-none bg-white dark:bg-black/20 rounded-bl-none text-text-primary'
            }`}>
              {m.text}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono ml-11">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></span>
            <span>VeriFi is drafting your response...</span>
          </div>
        )}

        {/* Step 1 Quick Bank Selector */}
        {messages.length === 1 && !isTyping && (
          <div className="flex flex-wrap gap-2 ml-11 mt-1">
            {['HDFC', 'SBI', 'ICICI', 'Axis', 'Kotak', 'PNB', 'Paytm Bank', 'Other'].map(b => (
              <button 
                key={b} 
                onClick={() => send(b)} 
                className="px-3.5 py-1.5 rounded-full border border-indigo-500/30 text-indigo-600 dark:text-indigo-300 hover:bg-indigo-500/15 transition-all text-xs font-medium bg-indigo-500/5 active:scale-95"
              >
                {b}
              </button>
            ))}
          </div>
        )}

        {/* Step 2 Txn ID Quick Skip */}
        {messages.length === 3 + offset && !isTyping && (
          <div className="flex flex-wrap gap-2 ml-11 mt-1">
            <button 
              onClick={() => send('skip')} 
              className="px-3.5 py-1.5 rounded-full border border-amber-500/30 text-amber-500 dark:text-amber-300 hover:bg-amber-500/15 transition-all text-xs font-medium bg-amber-500/5"
            >
              I don't have it right now / Skip
            </button>
          </div>
        )}

        {/* Step 3 Amount Quick Chips */}
        {messages.length === 5 + offset && !isTyping && (
          <div className="flex flex-wrap gap-2 ml-11 mt-1">
            {['₹1,000', '₹5,000', '₹10,000', '₹25,000', '₹50,000+'].map(amt => (
              <button 
                key={amt} 
                onClick={() => send(amt)} 
                className="px-3.5 py-1.5 rounded-full border border-indigo-500/30 text-indigo-600 dark:text-indigo-300 hover:bg-indigo-500/15 transition-all text-xs font-medium bg-indigo-500/5"
              >
                {amt}
              </button>
            ))}
          </div>
        )}

        {/* Step 4 Time Quick Chips */}
        {messages.length === 7 + offset && !isTyping && (
          <div className="flex flex-wrap gap-2 ml-11 mt-1">
            {['Within last 1 hour', 'Earlier today', 'Yesterday', 'A few days ago'].map(t => (
              <button 
                key={t} 
                onClick={() => send(t)} 
                className="px-3.5 py-1.5 rounded-full border border-indigo-500/30 text-indigo-600 dark:text-indigo-300 hover:bg-indigo-500/15 transition-all text-xs font-medium bg-indigo-500/5"
              >
                {t}
              </button>
            ))}
          </div>
        )}

        <div ref={chatBottomRef} />
      </div>

      {/* Input Bar */}
      <div className="p-3 sm:p-4 border-t border-border-glass flex gap-2 sm:gap-3 bg-black/5 dark:bg-black/20">
        <input 
          type="text" 
          value={input} 
          disabled={isTyping}
          onChange={e => setInput(e.target.value)} 
          onKeyDown={e => e.key === 'Enter' && send()}
          className="flex-1 bg-white/70 dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 transition-colors text-sm sm:text-base disabled:opacity-50" 
          placeholder="Type your reply here..."
        />
        <button 
          onClick={() => send()} 
          disabled={isTyping || !input.trim()}
          className="w-11 h-11 sm:w-12 sm:h-12 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 flex items-center justify-center text-white transition-colors shrink-0 shadow-md"
        >
          <Send size={18}/>
        </button>
      </div>
    </div>
  );
}
