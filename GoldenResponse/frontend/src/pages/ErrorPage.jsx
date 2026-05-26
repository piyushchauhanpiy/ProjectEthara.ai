import { Link } from 'react-router-dom';
import { Compass } from 'lucide-react';

export default function ErrorPage() {
  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center text-center px-4 pt-24">
      <Compass className="w-20 h-20 text-slate-500 animate-pulse mb-6" />
      <h1 className="text-4xl font-black dark:text-white mb-2">404 — Page Not Found</h1>
      <p className="text-slate-400 text-sm mb-6">The page you requested does not exist.</p>
      <Link
        to="/"
        className="px-6 py-3 rounded-xl bg-emerald-500 text-white font-bold shadow-lg hover:bg-emerald-600 transition"
      >
        Back to Home
      </Link>
    </div>
  );
}
