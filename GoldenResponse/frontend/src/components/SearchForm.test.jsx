import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SearchForm from './SearchForm';

describe('SearchForm', () => {
  it('shows error when ticker is empty', () => {
    const onSearch = vi.fn();
    render(<SearchForm onSearch={onSearch} isLoading={false} />);
    fireEvent.click(screen.getByRole('button', { name: /search/i }));
    expect(screen.getByText(/ticker symbol is required/i)).toBeInTheDocument();
    expect(onSearch).not.toHaveBeenCalled();
  });

  it('calls onSearch with uppercase ticker', () => {
    const onSearch = vi.fn();
    render(<SearchForm onSearch={onSearch} isLoading={false} submitLabel="Go" />);
    fireEvent.change(screen.getByLabelText(/ticker/i), { target: { value: 'aapl' } });
    fireEvent.click(screen.getByRole('button', { name: /go/i }));
    expect(onSearch).toHaveBeenCalledWith({ ticker: 'AAPL', date: undefined });
  });
});
