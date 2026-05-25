import React, { createContext, useContext, useEffect, useState } from 'react';

const StockContext = createContext(null);

const HISTORY_KEY = 'searchHistory';
const WATCHLIST_KEY = 'watchlist';
const THEME_KEY = 'theme';

export function StockProvider({ children }) {
  const [theme, setTheme] = useState(() => localStorage.getItem(THEME_KEY) || 'dark');
  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
    } catch {
      return [];
    }
  });
  const [watchlist, setWatchlist] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(WATCHLIST_KEY)) || [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'light' ? 'dark' : 'light'));

  const addToHistory = (ticker) => {
    const term = ticker.toUpperCase().trim();
    if (!term) return;
    setHistory((prev) => {
      const next = [term, ...prev.filter((t) => t !== term)].slice(0, 10);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
      return next;
    });
  };

  const toggleWatchlist = (ticker) => {
    const term = ticker.toUpperCase().trim();
    setWatchlist((prev) => {
      const exists = prev.includes(term);
      const next = exists ? prev.filter((t) => t !== term) : [...prev, term].slice(0, 20);
      localStorage.setItem(WATCHLIST_KEY, JSON.stringify(next));
      return next;
    });
  };

  const isInWatchlist = (ticker) => watchlist.includes(ticker.toUpperCase().trim());

  return (
    <StockContext.Provider
      value={{
        theme,
        toggleTheme,
        history,
        addToHistory,
        watchlist,
        toggleWatchlist,
        isInWatchlist,
      }}
    >
      {children}
    </StockContext.Provider>
  );
}

export function useStock() {
  const ctx = useContext(StockContext);
  if (!ctx) throw new Error('useStock must be used within StockProvider');
  return ctx;
}

export default StockContext;
