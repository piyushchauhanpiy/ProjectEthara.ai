import React from 'react';
import { Link } from 'react-router-dom';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error('UI Error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4">
          <h2 className="text-2xl font-bold dark:text-white mb-2">Something went wrong</h2>
          <p className="text-slate-400 mb-4">Please refresh or return home.</p>
          <Link
            to="/"
            className="px-6 py-3 rounded-xl bg-emerald-500 text-white font-semibold hover:bg-emerald-600"
          >
            Go Home
          </Link>
        </div>
      );
    }
    return this.props.children;
  }
}
