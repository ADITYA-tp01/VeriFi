import { useState, useRef, useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Shield, ShieldAlert, Cpu, CheckCircle2, AlertTriangle, FileWarning, Info } from 'lucide-react';
import Header from './components/Header';
import Hero from './components/Hero';
import ScenarioChips from './components/ScenarioChips';
import AgentTrace from './components/AgentTrace';
import ScoreGauge from './components/ScoreGauge';
import MismatchPanel from './components/MismatchPanel';
import RiskFactors from './components/RiskFactors';
import IncidentChat from './components/IncidentChat';
import PlaybookDeck from './components/PlaybookDeck';
import Footer from './components/Footer';

gsap.registerPlugin(ScrollTrigger);

export default function App() {
  const [mode, setMode] = useState<'analyze' | 'incident'>('analyze');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [status, setStatus] = useState<'landing' | 'analyzing' | 'result'>('landing');
  const [resultData, setResultData] = useState<any>(null);

  const [incidentData, setIncidentData] = useState<any>(null);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // Real API connection
  const runInvestigation = async (type: string, data: any) => {
    setStatus('analyzing');
    try {
      const formData = new FormData();
      if (type === 'qr' && data instanceof File) {
        formData.append('qr_image', data);
      } else {
        formData.append('user_input', data);
      }

      const res = await fetch('/api/analyze', {
        method: 'POST',
        body: formData
      });
      const resData = await res.json();
      
      // Map backend response to UI structure
      const bd = resData.result.score_breakdown || {};
      const factors = [];
      if (bd.upi) factors.push({ cat: 'UPI', desc: 'UPI analysis', pts: bd.upi });
      if (bd.url) factors.push({ cat: 'URL', desc: 'URL analysis', pts: bd.url });
      if (bd.social) factors.push({ cat: 'SOCIAL', desc: 'Social engineering', pts: bd.social });

      const getField = (obj: any, field: string) => {
        if (!obj) return 'Unknown';
        if (typeof obj === 'string') return obj;
        return obj[field] || 'Unknown';
      };

      setResultData({
        score: resData.result.score,
        level: resData.result.risk_level,
        mismatch: resData.result.evidence_vector?.intent_mechanism_mismatch || false,
        intent: getField(resData.result.intent, 'category'),
        mechanism: getField(resData.result.mechanism, 'action'),
        factors: factors.length > 0 ? factors : [{ cat: 'INFO', desc: 'General risk factors', pts: resData.result.score }],
        raw: resData.result
      });
      
      setStatus('result');
    } catch (error) {
      console.error(error);
      setStatus('landing');
    }
  };

  return (
    <div className="min-h-screen flex flex-col relative text-text-primary transition-colors duration-300">
      <div className="bg-orbs"></div>
      
      <Header mode={mode} setMode={(m) => { setMode(m); setIncidentData(null); }} theme={theme} setTheme={setTheme} />
      
      <main className="flex-1 w-full max-w-[1200px] mx-auto px-6 pt-24 pb-16 flex flex-col gap-8">
        {mode === 'analyze' ? (
          <>
            {status === 'landing' && (
              <>
                <Hero onRun={runInvestigation} />
                <ScenarioChips onRun={runInvestigation} />
              </>
            )}
            
            {status === 'analyzing' && (
              <AgentTrace docked={false} />
            )}

            {status === 'result' && resultData && (
              <div className="flex flex-col gap-6">
                <div className="flex items-center justify-between glass-panel px-8 py-4 border-risk-critical/30 shadow-[0_0_40px_rgba(239,68,68,0.1)]">
                  <div className="flex flex-col gap-1">
                    <span className="text-risk-critical font-bold tracking-wider uppercase text-sm flex items-center gap-2">
                      <AlertTriangle size={18}/> CRITICAL RISK
                    </span>
                    <h2 className="text-2xl md:text-3xl font-display font-semibold">Do not proceed with this payment.</h2>
                  </div>
                  <ScoreGauge score={resultData.score} level={resultData.level} />
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 flex flex-col gap-6">
                    <MismatchPanel intent={resultData.intent} mechanism={resultData.mechanism} mismatch={resultData.mismatch} />
                    <RiskFactors factors={resultData.factors} />
                  </div>
                  <div className="lg:col-span-1 h-full">
                    <AgentTrace docked={true} traceLog={resultData.raw.trace_log} />
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="glass-panel p-6 border-risk-critical/20 bg-risk-critical/5">
                    <h3 className="text-xl font-display font-medium mb-6 text-risk-critical">🚨 What to do right now</h3>
                    <ul className="flex flex-col gap-4">
                      <li className="flex items-start gap-3">
                        <input type="checkbox" className="mt-1 w-5 h-5 accent-risk-critical cursor-pointer" /> 
                        <span className="text-lg">Do not scan the QR or authorize any payment.</span>
                      </li>
                      <li className="flex items-start gap-3">
                        <input type="checkbox" className="mt-1 w-5 h-5 accent-risk-critical cursor-pointer" /> 
                        <span className="text-lg">Report the number to 1930.</span>
                      </li>
                    </ul>
                  </div>
                  <div className="glass-panel p-6 bg-[#0a0a0a] dark:bg-black/40 border-white/5">
                    <details className="group cursor-pointer">
                      <summary className="text-text-muted font-mono text-xs uppercase tracking-widest outline-none flex items-center justify-between opacity-70 hover:opacity-100 transition-opacity">
                        <span>Advanced / Technical Evidence (JSON)</span>
                        <span className="group-open:rotate-180 transition-transform duration-300">▼</span>
                      </summary>
                      <div className="mt-4 border-t border-white/10 pt-4 font-mono text-xs overflow-auto text-emerald-400/80 max-h-[300px]">
                        <pre>{JSON.stringify(resultData, null, 2)}</pre>
                      </div>
                    </details>
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 h-[70vh]">
            <IncidentChat onComplete={setIncidentData} />
            {incidentData ? (
              <PlaybookDeck incidentData={incidentData} />
            ) : (
              <div className="hidden md:flex flex-col items-center justify-center glass-panel h-full border-dashed border-2 border-indigo-500/20 bg-indigo-500/5 text-indigo-500">
                <ShieldAlert size={48} className="mb-4 opacity-50" />
                <p className="text-lg font-medium text-center px-8 opacity-80">Answer the questions on the left<br/>to generate your official Complaint Kit.</p>
              </div>
            )}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
