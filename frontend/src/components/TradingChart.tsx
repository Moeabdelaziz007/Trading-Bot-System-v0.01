"use client";
import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, IChartApi } from 'lightweight-charts';

interface CandleData {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume?: number;
}

interface TradingChartProps {
    symbol?: string;
    timeframe?: string;
    hideControls?: boolean;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://trading-brain-v1.amrikyy.workers.dev";
const SYSTEM_KEY = process.env.NEXT_PUBLIC_SYSTEM_KEY || "";

export function TradingChart({ symbol = "SPY", timeframe = "1H", hideControls = false }: TradingChartProps) {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [priceChange, setPriceChange] = useState({ value: 0, percent: 0 });

    useEffect(() => {
        const fetchAndRenderChart = async () => {
            if (!chartContainerRef.current) return;

            setLoading(true);
            setError(null);

            try {
                // Fetch real data from API with auth
                const res = await fetch(`${API_BASE}/api/candles?symbol=${symbol}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...(SYSTEM_KEY && { 'X-System-Key': SYSTEM_KEY })
                    }
                });
                const data = await res.json();

                let candles: CandleData[] = data.candles || [];

                // If no data, generate demo
                if (candles.length === 0) {
                    candles = generateDemoCandles(symbol);
                }

                // Calculate price change
                if (candles.length >= 2) {
                    const first = candles[0].close;
                    const last = candles[candles.length - 1].close;
                    const change = last - first;
                    const percent = (change / first) * 100;
                    setPriceChange({ value: change, percent });
                }

                // Clear existing chart
                if (chartRef.current) {
                    chartRef.current.remove();
                    chartRef.current = null;
                }

                // Create chart
                const chart = createChart(chartContainerRef.current, {
                    layout: {
                        background: { type: ColorType.Solid, color: '#0a0a0a' },
                        textColor: '#6b7280',
                    },
                    grid: {
                        vertLines: { color: '#1f293715' },
                        horzLines: { color: '#1f293715' },
                    },
                    crosshair: {
                        mode: 1,
                        vertLine: { color: '#22d3ee40', labelBackgroundColor: '#22d3ee' },
                        horzLine: { color: '#22d3ee40', labelBackgroundColor: '#22d3ee' },
                    },
                    rightPriceScale: { borderColor: '#1f2937' },
                    timeScale: { borderColor: '#1f2937', timeVisible: true },
                    width: chartContainerRef.current.clientWidth,
                    height: chartContainerRef.current.clientHeight,
                });

                chartRef.current = chart;

                // Add candlestick series
                const candleSeries = chart.addCandlestickSeries({
                    upColor: '#22c55e',
                    downColor: '#ef4444',
                    borderVisible: false,
                    wickUpColor: '#22c55e',
                    wickDownColor: '#ef4444',
                });

                // Add volume series
                const volumeSeries = chart.addHistogramSeries({
                    priceFormat: { type: 'volume' },
                    priceScaleId: '',
                });
                volumeSeries.priceScale().applyOptions({
                    scaleMargins: { top: 0.85, bottom: 0 },
                });

                // Format and set data
                const formattedCandles = candles.map(c => ({
                    time: c.time as string,
                    open: c.open,
                    high: c.high,
                    low: c.low,
                    close: c.close,
                }));

                const volumeData = candles.map(c => ({
                    time: c.time as string,
                    value: c.volume || Math.random() * 1000000,
                    color: c.close > c.open ? '#22c55e30' : '#ef444430',
                }));

                candleSeries.setData(formattedCandles);
                volumeSeries.setData(volumeData);
                chart.timeScale().fitContent();

                setLoading(false);
            } catch (err) {
                console.error('Chart error:', err);
                setError('Failed to load chart data');
                setLoading(false);
            }
        };

        fetchAndRenderChart();

        // Resize handler
        const handleResize = () => {
            if (chartContainerRef.current && chartRef.current) {
                chartRef.current.applyOptions({
                    width: chartContainerRef.current.clientWidth,
                    height: chartContainerRef.current.clientHeight,
                });
            }
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            if (chartRef.current) {
                chartRef.current.remove();
                chartRef.current = null;
            }
        };
    }, [symbol, timeframe]);

    return (
        <div className="relative w-full h-full rounded-xl overflow-hidden bg-[#0a0a0a] border border-gray-800/50">
            {/* Header - Hidden in War Room mode */}
            {!hideControls && (
                <>
                    <div className="absolute top-4 left-4 z-10 flex items-center gap-3">
                        <div className="bg-black/70 backdrop-blur-sm px-4 py-2 rounded-lg border border-gray-700/50 flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                            <span className="text-cyan-400 font-bold">{symbol}</span>
                            <span className="text-gray-500 text-sm">{timeframe}</span>
                        </div>

                        {/* Timeframe buttons */}
                        <div className="flex gap-1 bg-black/50 backdrop-blur-sm rounded-lg p-1 border border-gray-800/50">
                            {['1m', '5m', '15m', '1H', '4H', '1D'].map((tf) => (
                                <button
                                    key={tf}
                                    className={`px-2 py-1 text-xs rounded transition-all ${tf === timeframe
                                        ? 'bg-cyan-500/20 text-cyan-400'
                                        : 'text-gray-500 hover:text-gray-300'
                                        }`}
                                >
                                    {tf}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Price change badge */}
                    <div className="absolute top-4 right-4 z-10">
                        <div className={`backdrop-blur-sm px-3 py-2 rounded-lg border ${priceChange.percent >= 0
                            ? 'bg-green-500/10 border-green-500/30'
                            : 'bg-red-500/10 border-red-500/30'
                            }`}>
                            <span className={priceChange.percent >= 0 ? 'text-green-400' : 'text-red-400'}>
                                {priceChange.percent >= 0 ? '+' : ''}{priceChange.percent.toFixed(2)}%
                            </span>
                        </div>
                    </div>
                </>
            )}

            {/* Loading state */}
            {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-[#0a0a0a]">
                    <div className="flex flex-col items-center gap-3">
                        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
                        <span className="text-gray-500 text-sm">Loading {symbol}...</span>
                    </div>
                </div>
            )}

            {/* Error state */}
            {error && (
                <div className="absolute inset-0 flex items-center justify-center bg-[#0a0a0a]">
                    <div className="text-red-400 text-sm">{error}</div>
                </div>
            )}

            {/* Chart container */}
            <div ref={chartContainerRef} className="w-full h-full" />
        </div>
    );
}

function generateDemoCandles(symbol: string): CandleData[] {
    const basePrice = symbol === 'SPY' ? 595 : symbol === 'AAPL' ? 245 : 100;
    const candles: CandleData[] = [];
    let price = basePrice;

    const now = new Date();
    for (let i = 100; i >= 0; i--) {
        const date = new Date(now.getTime() - i * 3600000);
        const dateStr = date.toISOString().split('T')[0];

        const open = price;
        const change = (Math.random() - 0.5) * 5;
        const close = open + change;
        const high = Math.max(open, close) + Math.random() * 2;
        const low = Math.min(open, close) - Math.random() * 2;
        const volume = Math.floor(Math.random() * 1000000) + 500000;

        candles.push({ time: dateStr, open, high, low, close, volume });
        price = close;
    }

    return candles;
}
