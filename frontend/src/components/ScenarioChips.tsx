export default function ScenarioChips({ onRun }: any) {
  const scenarios = [
    { label: "Cashback QR", desc: "Claims to pay you, actually debits your account.", score: "CRITICAL", textClass: "text-risk-critical", bgClass: "bg-risk-critical", payload: "Congratulations! You have won ₹5000 cashback. Scan to receive your money immediately: upi://pay?pa=scammer@ybl&pn=Cashback&am=5000" },
    { label: "Electricity Bill Update", desc: "Fake URL impersonating official power board.", score: "HIGH", textClass: "text-risk-high", bgClass: "bg-risk-high", payload: "Dear Customer, your electricity power will be disconnected at 9:30 PM tonight from electricity office due to pending update. Click here to update immediately: http://bit.ly/update-bill-93022" },
    { label: "Lottery Winnings", desc: "Asks for advance fee to release funds.", score: "SUSPICIOUS", textClass: "text-risk-suspicious", bgClass: "bg-risk-suspicious", payload: "You have won $1,000,000 in the international lottery! Please transfer a processing fee of ₹2000 to upi://pay?pa=fees@sbi to claim your winnings immediately." },
    { label: "Local Merchant", desc: "Standard UPI payment to verified vendor.", score: "CLEAN", textClass: "text-risk-clean", bgClass: "bg-risk-clean", payload: "Hi, please pay ₹250 for the groceries at local shop." },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6 w-full">
      {scenarios.map((sc, i) => (
        <button key={i} onClick={() => onRun('text', sc.payload)} className="glass-panel p-5 flex flex-col items-start gap-2 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgba(0,0,0,0.12)] transition-all duration-300 group cursor-pointer text-left w-full relative overflow-hidden pl-6">
          <div className={`absolute top-0 left-0 w-1.5 h-full ${sc.bgClass}`}></div>
          <span className={`text-[10px] font-mono font-bold px-2 py-1 rounded-md ${sc.bgClass}/10 ${sc.textClass}`}>{sc.score}</span>
          <span className="text-[16px] font-bold mt-1 group-hover:text-blue-500 transition-colors leading-snug text-text-primary">{sc.label}</span>
          <span className="text-[13px] text-text-muted leading-tight mt-1">{sc.desc}</span>
        </button>
      ))}
    </div>
  );
}
