export default function ScoreGauge({ score, level }: any) {
  const isCritical = level === 'CRITICAL';
  const colorClass = isCritical ? 'text-risk-critical' : level === 'HIGH' ? 'text-risk-high' : level === 'SUSPICIOUS' ? 'text-risk-suspicious' : 'text-risk-clean';
  const strokeColor = isCritical ? '#EF4444' : level === 'HIGH' ? '#F97316' : level === 'SUSPICIOUS' ? '#EAB308' : '#10B981';
  const percentage = Math.min(100, Math.max(0, (score / 135) * 100));

  return (
    <div className="relative w-48 h-48 flex items-center justify-center">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="6" className="text-white/5" />
        <circle 
          cx="50" cy="50" r="45" fill="none" stroke={strokeColor} strokeWidth="6" 
          strokeDasharray="283" strokeDashoffset={283 - (283 * percentage) / 100}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-5xl font-bold">{score}</span>
        <span className="font-mono text-sm text-text-muted">/ 135</span>
      </div>
    </div>
  );
}
