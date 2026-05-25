import { useNavigate } from 'react-router-dom';
import { ArrowUpRight, History, Shield, Zap } from 'lucide-react';
import { useStock } from '../context/StockContext';

export default function HomePage() {
  const { history, watchlist } = useStock();
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4 pt-24 gradient-bg">
      <div className="text-center max-w-2xl mb-12">
        <h1 className="text-4xl md:text-6xl font-black bg-gradient-to-r from-emerald-400 via-teal-500 to-indigo-500 bg-clip-text text-transparent mb-4">
          Stock Market Dashboard
        </h1>
        <p className="text-slate-600 dark:text-slate-400 text-lg">
          Live quotes and historical OHLC data for stocks and commodities.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-3xl mb-12">
        <button
          type="button"
          onClick={() => navigate('/live')}
          className="glass p-6 rounded-2xl shadow-xl text-left hover:border-emerald-500/30 border border-transparent transition group"
        >
          <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center mb-4">
            <Zap className="w-6 h-6 text-emerald-400" />
          </div>
          <h3 className="text-xl font-bold dark:text-white mb-2 flex justify-between items-center">
            Live Price
            <ArrowUpRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition" />
          </h3>
          <p className="text-sm text-slate-400">Real-time price, volume, and market state.</p>
        </button>

        <button
          type="button"
          onClick={() => navigate('/historical')}
          className="glass p-6 rounded-2xl shadow-xl text-left hover:border-indigo-500/30 border border-transparent transition group"
        >
          <div className="w-12 h-12 bg-indigo-500/10 rounded-xl flex items-center justify-center mb-4">
            <Shield className="w-6 h-6 text-indigo-400" />
          </div>
          <h3 className="text-xl font-bold dark:text-white mb-2 flex justify-between items-center">
            Historical Data
            <ArrowUpRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition" />
          </h3>
          <p className="text-sm text-slate-400">OHLC for any past trading day. Weekends return Market Closed.</p>
        </button>
      </div>

      {(history.length > 0 || watchlist.length > 0) && (
        <div className="w-full max-w-3xl glass p-6 rounded-2xl shadow-lg space-y-4">
          {watchlist.length > 0 && (
            <div>
              <h4 className="text-sm font-bold text-slate-400 uppercase mb-3">Watchlist</h4>
              <div className="flex flex-wrap gap-2">
                {watchlist.map((ticker) => (
                  <button
                    key={ticker}
                    type="button"
                    onClick={() => navigate(`/live?ticker=${ticker}`)}
                    className="px-4 py-2 text-xs font-bold rounded-xl bg-amber-500/20 text-amber-500 hover:bg-amber-500 hover:text-white transition"
                  >
                    {ticker}
                  </button>
                ))}
              </div>
            </div>
          )}
          {history.length > 0 && (
            <div>
              <h4 className="text-sm font-bold text-slate-400 uppercase mb-3 flex items-center gap-2">
                <History className="w-4 h-4" /> Recent Searches
              </h4>
              <div className="flex flex-wrap gap-2">
                {history.map((ticker) => (
                  <button
                    key={ticker}
                    type="button"
                    onClick={() => navigate(`/live?ticker=${ticker}`)}
                    className="px-4 py-2 text-xs font-bold rounded-xl bg-slate-200/50 dark:bg-slate-800/80 hover:bg-emerald-500 hover:text-white dark:text-slate-300 transition"
                  >
                    {ticker}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
