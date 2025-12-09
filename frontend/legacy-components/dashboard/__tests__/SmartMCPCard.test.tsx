import React from 'react';
import { render, screen } from '@testing-library/react';
import { SmartMCPCard } from '../SmartMCPCard';
import '@testing-library/jest-dom';

// Mock the hook directly to avoid SWR/Async complexity in component testing
jest.mock('@/lib/hooks/useSmartMCP', () => ({
  useSmartMCP: jest.fn(),
}));

import { useSmartMCP } from '@/lib/hooks/useSmartMCP';

describe('SmartMCPCard', () => {
  it('renders loading state', () => {
    (useSmartMCP as jest.Mock).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    });

    render(<SmartMCPCard symbol="BTC" />);
    // Check for the loading skeleton class
    // The exact implementation uses 'animate-pulse'
    const skeleton = document.querySelector('.animate-pulse');
    expect(skeleton).toBeInTheDocument();
  });

  it('renders error state', () => {
    (useSmartMCP as jest.Mock).mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed'),
    });

    render(<SmartMCPCard symbol="BTC" />);
    expect(screen.getByText('BTC: Error loading')).toBeInTheDocument();
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('renders data correctly', () => {
    const mockData = {
      symbol: "BTC",
      asset_type: "crypto",
      price: {
          current: 50000,
          change_pct: 0.05,
          source: "test"
      },
      composite_signal: {
        direction: 'STRONG_BUY',
        confidence: 0.95,
        factors: ['Momentum'],
      },
    };

    (useSmartMCP as jest.Mock).mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
    });

    render(<SmartMCPCard symbol="BTC" />);

    expect(screen.getByText('BTC')).toBeInTheDocument();
    expect(screen.getByText('crypto')).toBeInTheDocument();
    // Use regex to match text that might be split
    expect(screen.getByText(/STRONG BUY/i)).toBeInTheDocument();
    // 0.05 * 100 = 5.00%
    expect(screen.getByText('+5.00%')).toBeInTheDocument();
    expect(screen.getByText('$50,000.00')).toBeInTheDocument();
  });
});
