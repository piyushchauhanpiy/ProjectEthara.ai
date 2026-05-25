import { AlertTriangle } from 'lucide-react';

export default function ErrorAlert({ message }) {
  if (!message) return null;
  return (
    <div
      role="alert"
      className="w-full max-w-xl flex items-center p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-500 dark:text-rose-400 text-sm font-medium animate-fade-in"
    >
      <AlertTriangle className="w-5 h-5 mr-3 shrink-0" />
      <span>{message}</span>
    </div>
  );
}
