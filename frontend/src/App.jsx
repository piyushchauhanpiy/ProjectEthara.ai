import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { StockProvider } from './context/StockContext';
import ErrorBoundary from './components/ErrorBoundary';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Loader from './components/Loader';

const HomePage = lazy(() => import('./pages/HomePage'));
const LivePage = lazy(() => import('./pages/LivePage'));
const HistoricalPage = lazy(() => import('./pages/HistoricalPage'));
const ErrorPage = lazy(() => import('./pages/ErrorPage'));

export default function App() {
  return (
    <StockProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-darkBg text-slate-900 dark:text-slate-100 transition-colors duration-300">
          <Navbar />
          <main className="flex-grow pb-12">
            <ErrorBoundary>
              <Suspense fallback={<Loader />}>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/live" element={<LivePage />} />
                  <Route path="/historical" element={<HistoricalPage />} />
                  <Route path="*" element={<ErrorPage />} />
                </Routes>
              </Suspense>
            </ErrorBoundary>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </StockProvider>
  );
}
