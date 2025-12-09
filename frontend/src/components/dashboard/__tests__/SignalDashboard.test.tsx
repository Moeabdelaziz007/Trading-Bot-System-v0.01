import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import SignalDashboard from '../SignalDashboard';
import '@testing-library/jest-dom';

// Mock Ably
jest.mock('ably', () => {
  return {
    Realtime: class {
      channels = {
        get: jest.fn().mockReturnValue({
          subscribe: jest.fn(),
          unsubscribe: jest.fn(),
        }),
      };
      close = jest.fn();
    },
  };
});

// Mock fetch
const mockSignals = [
  {
    id: 1,
    symbol: 'BTC/USD',
    direction: 'BUY',
    confidence: 0.85,
    price: 50000,
    timestamp: '2023-01-01T12:00:00Z',
    factors: 'RSI Oversold',
    asset_type: 'crypto',
    source: 'test'
  },
];

describe('SignalDashboard', () => {
  beforeEach(() => {
    (global.fetch as jest.Mock).mockClear();
  });

  it('renders loading state initially', () => {
    // Mock fetch to pending
    (global.fetch as jest.Mock).mockReturnValue(new Promise(() => {}));
    render(<SignalDashboard />);
    // Check for spinner or loading text
    // The component uses an animate-spin class
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('fetches and displays signals', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'success', signals: mockSignals }),
    });

    render(<SignalDashboard />);

    await waitFor(() => {
      // Use query by text carefully, sometimes it might match multiple
      // "BTC/USD" is in the symbol column
      const symbolElements = screen.getAllByText('BTC/USD');
      expect(symbolElements.length).toBeGreaterThan(0);

      // "BUY" might be part of "STRONG BUY" or just "BUY"
      // The emoji might also be there. The text content is "📈 BUY"
      // We can search for just "BUY" loosely
      expect(screen.getByText(/BUY/)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('Connection error'));

    render(<SignalDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Connection error')).toBeInTheDocument();
    });
  });
});
