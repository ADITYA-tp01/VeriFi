export default function ScoreGauge({ score, level }: any) {
  const isCritical = level === 'CRITICAL';
  const isHigh = level === 'HIGH';
  const isSuspicious = level === 'SUSPICIOUS';

  const strokeColor = isCritical ? '#EF4444' : isHigh ? '#F97316' : isSuspicious ? '#EAB308' : '#10B981';
  const percentage = Math.min(100, Math.max(0, (score / 135) * 100));

  const tierBadge = isCritical ? 'bg-risk-critical/15 text-risk-critical border-risk-critical/30' :
    isHigh ? 'bg-amber-500/15 text-amber-400 border-amber-500/30' :
    isSuspicious ? 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30' :
    'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-44 h-44 flex items-center justify-center">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="44" fill="none" stroke="currentColor" strokeWidth="6" className="text-white/5 dark:text-white/10" />
          <circle 
            cx="50" cy="50" r="44" fill="none" stroke={strokeColor} strokeWidth="6" 
            strokeDasharray="276" strokeDashoffset={276 - (276 * percentage) / 100}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="flex items-baseline">
            <span className="font-mono text-4xl font-bold tracking-tight">{Math.round(percentage)}</span>
            <span className="font-mono text-xl text-text-muted ml-0.5">%</span>
          </div>
          <span className="text-[11px] font-mono text-text-muted mt-0.5">{score} / 135 pts</span>
        </div>
      </div>
      <span className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-bold uppercase tracking-wider border ${tierBadge}`}>
        {level || 'EVALUATED'}
      </span>
    </div>
  );
}
