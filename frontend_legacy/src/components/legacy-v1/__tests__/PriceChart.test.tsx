import React from 'react';
import { render, screen } from '@testing-library/react';
import { PriceChart } from '../PriceChart';
import '@testing-library/jest-dom';

// Simplify Recharts mock to avoid SVG issues
// We mock nested components as simple divs to avoid JSDOM warnings about SVG tags
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  AreaChart: ({ children }: any) => <div data-testid="area-chart">{children}</div>,
  Area: () => <div data-testid="area" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  defs: ({ children }: any) => <div data-testid="defs">{children}</div>,
  linearGradient: ({ children }: any) => <div data-testid="linear-gradient">{children}</div>,
  stop: () => <div data-testid="stop" />,
}));

describe('PriceChart', () => {
  // Suppress console.error for specific React warnings if they persist
  const originalError = console.error;
  beforeAll(() => {
    console.error = (...args) => {
      if (/Warning.*(linearGradient|defs)/.test(args[0])) return;
      originalError(...args);
    };
  });

  afterAll(() => {
    console.error = originalError;
  });

  it('renders chart container', () => {
    render(<PriceChart />);
    expect(screen.getByText('BTC/USDT')).toBeInTheDocument();
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
  });

  it('renders timeframes', () => {
    render(<PriceChart />);
    expect(screen.getByText('1H')).toBeInTheDocument();
    expect(screen.getByText('1D')).toBeInTheDocument();
  });
});
