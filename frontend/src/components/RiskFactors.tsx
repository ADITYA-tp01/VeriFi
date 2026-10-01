export default function RiskFactors({ factors }: any) {
  return (
    <div className="glass-panel p-6 flex flex-col gap-6">
      <h3 className="text-xl font-display font-medium">Risk Factors Breakdown</h3>
      <div className="flex flex-col gap-3 w-full">
        {factors.map((f: any, i: number) => (
          <div key={i} className="flex items-center justify-between px-4 py-3 sm:py-4 rounded-xl bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 hover:bg-black/10 dark:hover:bg-white/10 transition-colors w-full">
            <div className="flex items-center gap-4">
              <span className="px-3 py-1 rounded-md bg-white/50 dark:bg-white/10 text-xs font-bold tracking-widest text-text-muted">{f.cat}</span>
              <span className="text-base font-medium">{f.desc}</span>
            </div>
            <span className="font-mono text-risk-critical font-bold text-lg">+{f.pts}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
