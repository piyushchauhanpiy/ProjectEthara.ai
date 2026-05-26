export default function Loader() {
  return (
    <div className="flex flex-col items-center space-y-4 py-12 animate-fade-in">
      <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
      <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
        Fetching market data...
      </p>
    </div>
  );
}
