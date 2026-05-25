import { useState } from 'react';
import { Search, Calendar } from 'lucide-react';

const TICKER_REGEX = /^[A-Za-z0-9=.-]{1,12}$/;

export default function SearchForm({
  includeDate = false,
  onSearch,
  isLoading,
  submitLabel = 'Search',
}) {
  const [ticker, setTicker] = useState('');
  const [date, setDate] = useState('');
  const [error, setError] = useState('');

  const today = new Date().toISOString().split('T')[0];

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    const trimmed = ticker.trim().toUpperCase();
    if (!trimmed) {
      setError('Ticker symbol is required.');
      return;
    }
    if (!TICKER_REGEX.test(trimmed)) {
      setError('Invalid ticker format. Use symbols like AAPL, GC=F, CL=F.');
      return;
    }

    if (includeDate) {
      if (!date) {
        setError('Please select a date.');
        return;
      }
      if (date > today) {
        setError('Future dates are not allowed.');
        return;
      }
    }

    onSearch({ ticker: trimmed, date });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-xl glass p-6 rounded-2xl shadow-xl flex flex-col space-y-4 animate-fade-in"
      noValidate
    >
      <div>
        <label htmlFor="ticker" className="block mb-2 text-sm font-medium text-slate-700 dark:text-slate-300">
          Ticker Symbol
        </label>
        <div className="relative">
          <Search className="absolute left-3 top-3.5 h-5 w-5 text-slate-400" />
          <input
            id="ticker"
            type="text"
            placeholder="e.g. AAPL, TSLA, GC=F"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            className="w-full pl-11 pr-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white/50 dark:bg-slate-800/50 text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 outline-none transition"
            disabled={isLoading}
            autoComplete="off"
          />
        </div>
      </div>

      {includeDate && (
        <div>
          <label htmlFor="date" className="block mb-2 text-sm font-medium text-slate-700 dark:text-slate-300">
            Historical Date
          </label>
          <div className="relative">
            <Calendar className="absolute left-3 top-3.5 h-5 w-5 text-slate-400" />
            <input
              id="date"
              type="date"
              max={today}
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full pl-11 pr-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white/50 dark:bg-slate-800/50 text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 outline-none transition"
              disabled={isLoading}
            />
          </div>
        </div>
      )}

      {error && <p className="text-rose-500 text-sm font-medium">{error}</p>}

      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold shadow-lg hover:from-emerald-600 hover:to-teal-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Loading...' : submitLabel}
      </button>
    </form>
  );
}
