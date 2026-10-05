import { ShieldAlert, Globe, MessageSquare, Zap, Activity } from 'lucide-react';

export default function RiskFactors({ factors }: any) {
  const getCategoryConfig = (cat: string) => {
    switch (cat.toUpperCase()) {
      case 'UPI':
        return { icon: Zap, color: 'text-amber-400 bg-amber-500/10 border-amber-500/20', label: 'UPI Protocol' };
      case 'URL':
        return { icon: Globe, color: 'text-blue-400 bg-blue-500/10 border-blue-500/20', label: 'Domain Intel' };
      case 'SOCIAL':
        return { icon: MessageSquare, color: 'text-purple-400 bg-purple-500/10 border-purple-500/20', label: 'Social Engineering' };
      default:
        return { icon: ShieldAlert, color: 'text-rose-400 bg-rose-500/10 border-rose-500/20', label: cat || 'Signal' };
    }
  };

  const totalPoints = factors.reduce((sum: number, f: any) => sum + (Number(f.pts) || 0), 0);

  return (
    <div className="glass-panel p-6 flex flex-col gap-5 border-white/10">
      <div className="flex items-center justify-between pb-3 border-b border-border-glass">
        <div className="flex items-center gap-2">
          <Activity size={18} className="text-risk-critical" />
          <h3 className="text-xl font-display font-medium text-text-primary">Multi-Layered Risk Vector Breakdown</h3>
        </div>
        <span className="text-xs font-mono text-text-muted bg-white/5 px-2.5 py-1 rounded-full border border-border-glass">
          {factors.length} Detected Factor{factors.length === 1 ? '' : 's'}
        </span>
      </div>

      <div className="flex flex-col gap-3 w-full">
        {factors.map((f: any, i: number) => {
          const config = getCategoryConfig(f.cat);
          const Icon = config.icon;
          const percentage = totalPoints > 0 ? Math.round(((Number(f.pts) || 0) / totalPoints) * 100) : 100;

          return (
            <div 
              key={i} 
              className="flex flex-col gap-2 p-4 rounded-xl bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 hover:border-white/10 transition-all"
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className={`p-1.5 rounded-lg border ${config.color} shrink-0`}>
                    <Icon size={16} />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-base font-semibold text-text-primary">{f.desc}</span>
                    <span className="text-xs font-mono text-text-muted">{config.label}</span>
                  </div>
                </div>
                <div className="flex items-baseline gap-1 text-right">
                  <span className="font-mono text-risk-critical font-bold text-lg">+{f.pts}</span>
                  <span className="text-xs text-text-muted font-mono">pts</span>
                </div>
              </div>

              {/* Impact progress bar */}
              <div className="w-full bg-black/20 dark:bg-black/40 h-1.5 rounded-full overflow-hidden mt-1">
                <div 
                  className="bg-gradient-to-r from-amber-500 to-rose-500 h-full rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, Math.max(10, percentage))}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
