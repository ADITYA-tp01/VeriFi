import { useState, useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ShieldAlert, AlertTriangle, ArrowLeft, RefreshCw, AlertCircle } from 'lucide-react';
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
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [incidentData, setIncidentData] = useState<any>(null);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const resetToLanding = () => {
    setStatus('landing');
    setResultData(null);
    setErrorMsg(null);
  };

  // Real API connection
  const runInvestigation = async (type: string, data: any) => {
    setStatus('analyzing');
    setErrorMsg(null);
    try {
      const formData = new FormData();
      if (type === 'qr' && data instanceof File) {
        formData.append('qr_image', data);
      } else {
        formData.append('user_input', data);
      }

      const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000';
      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        throw new Error(`API returned status ${res.status}: ${res.statusText}`);
      }

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
    } catch (error: any) {
      console.error(error);
      setErrorMsg(error?.message || "Failed to complete investigation. Please ensure backend service is active.");
      setStatus('landing');
    }
  };

  return (
    <div className="min-h-screen flex flex-col relative text-text-primary transition-colors duration-300">
      <div className="bg-orbs"></div>
      
      <Header mode={mode} setMode={(m: 'analyze' | 'incident') => { setMode(m); setIncidentData(null); }} theme={theme} setTheme={setTheme} />
      
      <main className="flex-1 w-full max-w-[1200px] mx-auto px-6 pt-24 pb-16 flex flex-col gap-8">
        {mode === 'analyze' ? (
          <>
            {errorMsg && (
              <div className="glass-panel p-4 border-red-500/30 bg-red-500/10 flex items-center justify-between gap-4 text-red-200 animate-fade-in">
                <div className="flex items-center gap-3">
                  <AlertCircle size={20} className="text-red-400 shrink-0" />
                  <span className="text-sm">{errorMsg}</span>
                </div>
                <button 
                  onClick={() => setErrorMsg(null)}
                  className="text-xs px-3 py-1 rounded bg-red-500/20 hover:bg-red-500/30 text-white font-mono transition-colors"
                >
                  Dismiss
                </button>
              </div>
            )}

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
              <div className="flex flex-col gap-6 animate-fade-in">
                {/* Back to Input Navigation Action */}
                <div className="flex items-center justify-between">
                  <button 
                    onClick={resetToLanding}
                    className="flex items-center gap-2 text-sm text-text-muted hover:text-text-primary px-3.5 py-1.5 rounded-lg border border-border-glass hover:bg-white/5 transition-colors font-medium"
                  >
                    <ArrowLeft size={16} /> Start New Scan
                  </button>
                  <span className="text-xs font-mono text-text-muted">Report finalized with cryptographic hash</span>
                </div>

                {/* Dashboard Top Telemetry & Severity Banner */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between glass-panel px-6 py-5 border-risk-critical/30 shadow-[0_0_40px_rgba(239,68,68,0.1)] gap-4">
                  <div className="flex flex-col gap-1.5">
                    <div className="flex items-center gap-3">
                      <span className="text-risk-critical font-bold tracking-wider uppercase text-xs sm:text-sm flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-risk-critical/10 border border-risk-critical/20">
                        <AlertTriangle size={16}/> {resultData.level} THREAT
                      </span>
                      <span className="text-text-muted text-xs font-mono">
                        ID: #VF-{Math.abs(resultData.score * 7919).toString(16).toUpperCase().slice(0, 6)}
                      </span>
                    </div>
                    <h2 className="text-2xl md:text-3xl font-display font-semibold">
                      {resultData.mismatch ? "Deceptive Intent Detected — Do Not Pay" : "Investigation Analysis Report"}
                    </h2>
                    <p className="text-sm text-text-muted">
                      Deterministic verification engine completed analysis with full evidence vector.
                    </p>
                  </div>
                  <div className="flex items-center gap-4 self-center sm:self-auto">
                    <ScoreGauge score={resultData.score} level={resultData.level} />
                  </div>
                </div>
                
                {/* Primary Analysis Dashboard Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 flex flex-col gap-6">
                    <MismatchPanel intent={resultData.intent} mechanism={resultData.mechanism} mismatch={resultData.mismatch} />
                    <RiskFactors factors={resultData.factors} />
                  </div>
                  <div className="lg:col-span-1 h-full">
                    <AgentTrace docked={true} traceLog={resultData.raw?.trace_log} />
                  </div>
                </div>

                {/* Immediate Remediation & Raw Evidence Deck */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="glass-panel p-6 border-risk-critical/20 bg-risk-critical/5">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl font-display font-medium text-risk-critical flex items-center gap-2">
                        <ShieldAlert size={20} /> Immediate Protective Steps
                      </h3>
                      <span className="text-xs font-mono text-risk-critical/80 bg-risk-critical/10 px-2 py-0.5 rounded">URGENT</span>
                    </div>
                    <ul className="flex flex-col gap-3.5">
                      <li className="flex items-start gap-3">
                        <input type="checkbox" id="step-qr" className="mt-1 w-5 h-5 accent-risk-critical cursor-pointer rounded" /> 
                        <label htmlFor="step-qr" className="text-base text-text-primary cursor-pointer leading-snug">
                          <strong>Halt payment:</strong> Do not scan any QR, authorize UPI mandates, or enter your PIN.
                        </label>
                      </li>
                      <li className="flex items-start gap-3">
                        <input type="checkbox" id="step-1930" className="mt-1 w-5 h-5 accent-risk-critical cursor-pointer rounded" /> 
                        <label htmlFor="step-1930" className="text-base text-text-primary cursor-pointer leading-snug">
                          <strong>Report incident:</strong> Dial National Cyber Crime Helpline <a href="tel:1930" className="text-blue-400 underline font-mono">1930</a> or visit cybercrime.gov.in.
                        </label>
                      </li>
                      <li className="flex items-start gap-3">
                        <input type="checkbox" id="step-bank" className="mt-1 w-5 h-5 accent-risk-critical cursor-pointer rounded" /> 
                        <label htmlFor="step-bank" className="text-base text-text-primary cursor-pointer leading-snug">
                          <strong>Notify bank:</strong> If money was already sent, request an immediate freeze/recall from your bank fraud desk.
                        </label>
                      </li>
                    </ul>
                  </div>
                  
                  <div className="glass-panel p-6 bg-[#0a0a0a] dark:bg-black/40 border-white/5 flex flex-col justify-between">
                    <div>
                      <h3 className="text-sm font-bold uppercase tracking-wider text-text-muted mb-2 font-mono">Audit & Forensics Payload</h3>
                      <p className="text-xs text-text-muted mb-4">Cryptographically bound execution trace and JSON evidence vector.</p>
                    </div>
                    <details className="group cursor-pointer">
                      <summary className="text-text-muted font-mono text-xs uppercase tracking-widest outline-none flex items-center justify-between p-2.5 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                        <span>Inspect Raw Evidence JSON</span>
                        <span className="group-open:rotate-180 transition-transform duration-300">▼</span>
                      </summary>
                      <div className="mt-3 border-t border-white/10 pt-3 font-mono text-xs overflow-auto text-emerald-400/90 max-h-[220px] bg-black/60 p-3 rounded-lg">
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
