"use client"

import { useEffect, useRef } from "react"

interface TradingChartProps {
    symbol?: string
    theme?: "dark" | "light"
}

export function TradingChart({ symbol = "BTCUSD", theme = "dark" }: TradingChartProps) {
    const containerRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (!containerRef.current) return

        // Clear previous widget content safely
        const container = containerRef.current
        container.innerHTML = ""

        // Create TradingView widget script
        const script = document.createElement("script")
        script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js"
        script.type = "text/javascript"
        script.async = true
        script.innerHTML = JSON.stringify({
            autosize: true,
            symbol: `BINANCE:${symbol}`,
            interval: "15",
            timezone: "Etc/UTC",
            theme: theme,
            style: "1",
            locale: "en",
            allow_symbol_change: true,
            calendar: false,
            support_host: "https://www.tradingview.com",
            hide_top_toolbar: false,
            hide_legend: false,
            save_image: false,
            backgroundColor: theme === "dark" ? "rgba(5, 5, 5, 1)" : "rgba(255, 255, 255, 1)",
            gridColor: theme === "dark" ? "rgba(57, 255, 20, 0.06)" : "rgba(0, 0, 0, 0.06)",
        })

        container.appendChild(script)

        return () => {
            if (container) {
                container.innerHTML = ""
            }
        }
    }, [symbol, theme])

    return (
        <div className="tradingview-widget-container h-full w-full min-h-[600px] rounded-lg border border-border bg-card overflow-hidden">
            <div id="tradingview_widget" ref={containerRef} className="h-full w-full" />
        </div>
    )
}
