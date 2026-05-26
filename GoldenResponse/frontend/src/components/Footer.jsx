export default function Footer() {
  return (
    <footer className="w-full py-6 mt-auto text-center border-t border-slate-200 dark:border-slate-800/60 text-xs font-medium text-slate-400">
      &copy; {new Date().getFullYear()} Equinox Stock Dashboard. Data via Yahoo Finance.
    </footer>
  );
}
