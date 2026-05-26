import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/stocks',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

API.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.message ||
      error.message ||
      'Network error. Please try again.';
    return Promise.reject({ ...error, displayMessage: message });
  }
);

export const fetchLivePrice = async (ticker) => {
  const { data } = await API.get(`/live/${encodeURIComponent(ticker)}`);
  return data?.data ?? data;
};

export const fetchHistoricalPrice = async (ticker, date) => {
  const { data } = await API.get('/history', {
    params: { ticker, date },
  });
  if (data?.message === 'Market Closed') {
    return { message: 'Market Closed' };
  }
  return data?.data ?? data;
};

export default API;
