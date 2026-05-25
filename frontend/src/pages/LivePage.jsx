import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import SearchForm from '../components/SearchForm';
import StockCard from '../components/StockCard';
import Loader from '../components/Loader';
import ErrorAlert from '../components/ErrorAlert';
import { fetchLivePrice } from '../services/api';
import { useStock } from '../context/StockContext';

export default function LivePage() {
  const [searchParams] = useSearchParams();
  const { addToHistory } = useStock();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const executeSearch = useCallback(
    async ({ ticker }) => {
      setLoading(true);
      setError('');
      setData(null);
      try {
        const res = await fetchLivePrice(ticker);
        setData(res);
        addToHistory(ticker);
        toast.success(`Loaded ${ticker}`);
      } catch (err) {
        const msg = err.displayMessage || err.response?.data?.message || 'Failed to fetch live data.';
        setError(msg);
        toast.error(msg);
      } finally {
        setLoading(false);
      }
    },
    [addToHistory]
  );

  useEffect(() => {
    const tickerParam = searchParams.get('ticker');
    if (tickerParam) {
      executeSearch({ ticker: tickerParam });
    }
  }, [searchParams, executeSearch]);

  return (
    <div className="flex flex-col items-center min-h-[85vh] pt-28 px-4 space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-black dark:text-white">Live Price Tracker</h2>
        <p className="text-sm text-slate-400 mt-1">AAPL, TSLA, GC=F, CL=F and more</p>
      </div>

      <SearchForm
        includeDate={false}
        onSearch={executeSearch}
        isLoading={loading}
        submitLabel="Get Live Price"
      />

      {loading && <Loader />}
      <ErrorAlert message={error} />
      {data && <StockCard data={data} />}
    </div>
  );
}
