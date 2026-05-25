export default function HistoricalTable({ data }) {
  const rows = [
    ['Ticker', data.ticker, 'font-bold text-emerald-500'],
    ['Date', data.date, 'font-mono'],
    ['Open', data.open?.toFixed(2), 'font-mono'],
    ['High', data.high?.toFixed(2), 'font-mono text-emerald-500'],
    ['Low', data.low?.toFixed(2), 'font-mono text-rose-500'],
    ['Close', data.close?.toFixed(2), 'font-mono font-bold'],
    ['Adj. Close', data.adjustedClose?.toFixed(2), 'font-mono text-indigo-400'],
    ['Volume', data.volume?.toLocaleString(), 'font-mono'],
  ];

  return (
    <div className="w-full max-w-xl glass rounded-2xl shadow-2xl overflow-hidden animate-fade-in">
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 px-6 py-4">
        <h3 className="text-white font-bold">Historical Snapshot</h3>
      </div>
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="bg-slate-200/50 dark:bg-slate-800/70 text-slate-400 uppercase text-xs">
            <th className="px-6 py-3">Metric</th>
            <th className="px-6 py-3 text-right">Value</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 dark:divide-slate-700 text-slate-700 dark:text-slate-200">
          {rows.map(([label, value, cls]) => (
            <tr key={label}>
              <td className="px-6 py-3 text-slate-400">{label}</td>
              <td className={`px-6 py-3 text-right ${cls || ''}`}>{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
