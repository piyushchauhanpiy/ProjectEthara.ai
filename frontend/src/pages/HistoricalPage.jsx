import { useState } from 'react';
import { Info } from 'lucide-react';
import toast from 'react-hot-toast';
import SearchForm from '../components/SearchForm';
import HistoricalTable from '../components/HistoricalTable';
import ChartSection from '../components/ChartSection';
import Loader from '../components/Loader';
import ErrorAlert from '../components/ErrorAlert';
import { fetchHistoricalPrice } from '../services/api';

export default function HistoricalPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [marketClosed, setMarketClosed] = useState(false);

  const executeSearch = async ({ ticker, date }) => {
    setLoading(true);
    setError('');
    setData(null);
    setMarketClosed(false);
    try {
      const res = await fetchHistoricalPrice(ticker, date);
      if (res?.message === 'Market Closed') {
        setMarketClosed(true);
        toast('Market Closed', { icon: 'ℹ️' });
      } else {
        setData(res);
        toast.success(`Historical data for ${ticker}`);
      }
    } catch (err) {
      const msg =
        err.displayMessage || err.response?.data?.message || 'Failed to fetch historical data.';
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center min-h-[85vh] pt-28 px-4 space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-black dark:text-white">Historical Data</h2>
        <p className="text-sm text-slate-400 mt-1">Select ticker and a past trading date</p>
      </div>

      <SearchForm
        includeDate
        onSearch={executeSearch}
        isLoading={loading}
        submitLabel="Get Historical Data"
      />

      {loading && <Loader />}
      <ErrorAlert message={error} />

      {marketClosed && (
        <div className="w-full max-w-xl flex items-center p-5 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-500 font-semibold animate-fade-in">
          <Info className="w-6 h-6 mr-3 shrink-0" />
          <div>
            <h5 className="text-base">Market Closed</h5>
            <p className="text-xs font-normal text-slate-400 mt-0.5">
              No trading data for this date (weekend, holiday, or non-trading day).
            </p>
          </div>
        </div>
      )}

      {data && (
        <div className="w-full flex flex-col items-center">
          <HistoricalTable data={data} />
          <ChartSection data={data} />
        </div>
      )}
    </div>
  );
}
