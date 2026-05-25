import { Link, NavLink } from 'react-router-dom';
import { Moon, Sun, TrendingUp } from 'lucide-react';
import { useStock } from '../context/StockContext';

const linkClass = ({ isActive }) =>
  isActive
    ? 'text-emerald-500 font-semibold'
    : 'text-slate-600 dark:text-slate-300 hover:text-emerald-400 transition';

export default function Navbar() {
  const { theme, toggleTheme } = useStock();

  return (
    <nav className="glass fixed top-0 left-0 w-full z-50 px-4 md:px-6 py-4 flex justify-between items-center shadow-md">
      <Link
        to="/"
        className="flex items-center space-x-2 text-lg md:text-xl font-bold tracking-wider text-slate-800 dark:text-white"
      >
        <TrendingUp className="text-emerald-500 w-6 h-6" />
        <span>EQUINOX</span>
      </Link>

      <div className="flex items-center space-x-4 md:space-x-6 text-sm md:text-base">
        <NavLink to="/" className={linkClass} end>
          Home
        </NavLink>
        <NavLink to="/live" className={linkClass}>
          Live
        </NavLink>
        <NavLink to="/historical" className={linkClass}>
          History
        </NavLink>
        <button
          type="button"
          onClick={toggleTheme}
          aria-label="Toggle theme"
          className="p-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-700 transition"
        >
          {theme === 'light' ? (
            <Moon className="w-5 h-5 text-slate-700" />
          ) : (
            <Sun className="w-5 h-5 text-amber-400" />
          )}
        </button>
      </div>
    </nav>
  );
}
