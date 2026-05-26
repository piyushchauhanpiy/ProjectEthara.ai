import { BarChart2, Star, TrendingDown, TrendingUp } from 'lucide-react';
import { useStock } from '../context/StockContext';

export default function StockCard({ data }) {
  const { toggleWatchlist, isInWatchlist } = useStock();
  const isPositive = data.currentPrice >= data.previousClose;
  const changePct = data.previousClose
    ? (((data.currentPrice - data.previousClose) / data.previousClose) * 100).toFixed(2)
    : '0.00';
  const inWatchlist = isInWatchlist(data.ticker);

  return (
    <div className="w-full max-w-xl glass rounded-2xl p-6 shadow-2xl transition hover:scale-[1.01] animate-fade-in">
      <div className="flex justify-between items-start border-b border-slate-200 dark:border-slate-700 pb-4">
        <div>
          <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white">{data.ticker}</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">{data.companyName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
              data.marketState === 'REGULAR'
                ? 'bg-emerald-500/20 text-emerald-500'
                : 'bg-amber-500/20 text-amber-500'
            }`}
          >
            {data.marketState}
          </span>
          <button
            type="button"
            onClick={() => toggleWatchlist(data.ticker)}
            aria-label="Toggle watchlist"
            className="p-2 rounded-lg hover:bg-slate-200/50 dark:hover:bg-slate-700/50"
          >
            <Star
              className={`w-5 h-5 ${inWatchlist ? 'fill-amber-400 text-amber-400' : 'text-slate-400'}`}
            />
          </button>
        </div>
      </div>

      <div className="my-6 flex justify-between items-center">
        <div>
          <span className="text-xs text-slate-400 uppercase font-semibold">Current Price</span>
          <div className="text-4xl font-black text-slate-900 dark:text-white mt-1">
            {data.currentPrice?.toFixed(2)}{' '}
            <span className="text-lg font-normal text-slate-400">{data.currency}</span>
          </div>
        </div>
        <div
          className={`flex items-center gap-1 px-3 py-2 rounded-xl text-sm font-bold ${
            isPositive ? 'text-emerald-500 bg-emerald-500/10' : 'text-rose-500 bg-rose-500/10'
          }`}
        >
          {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          <span>{changePct}%</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm bg-slate-100/50 dark:bg-slate-800/40 p-4 rounded-xl">
        <div className="flex justify-between">
          <span className="text-slate-400">Open</span>
          <span className="font-semibold dark:text-white">{data.open?.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Prev Close</span>
          <span className="font-semibold dark:text-white">{data.previousClose?.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">High</span>
          <span className="font-semibold text-emerald-500">{data.high?.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Low</span>
          <span className="font-semibold text-rose-500">{data.low?.toFixed(2)}</span>
        </div>
        <div className="flex justify-between col-span-2 border-t border-slate-200 dark:border-slate-700 pt-2">
          <span className="text-slate-400 flex items-center gap-1">
            <BarChart2 className="w-4 h-4" /> Volume
          </span>
          <span className="font-semibold dark:text-white">
            {data.volume?.toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  );
}
