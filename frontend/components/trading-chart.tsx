"use client"

import { useEffect, useRef, useState } from "react"

interface TradingChartProps {
    symbol?: string
    theme?: "dark" | "light"
}

export function TradingChart({ symbol = "BTCUSD", theme = "dark" }: TradingChartProps) {
    const containerRef = useRef<HTMLDivElement>(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        if (!containerRef.current) return

        // Clear previous widget content safely
        const container = containerRef.current
        container.innerHTML = ""
        setIsLoading(true)

        // Create proper TradingView widget container structure
        const widgetDiv = document.createElement("div")
        widgetDiv.className = "tradingview-widget-container__widget"
        widgetDiv.style.height = "100%"
        widgetDiv.style.width = "100%"
        container.appendChild(widgetDiv)

        // Create TradingView widget script
        const script = document.createElement("script")
        script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js"
        script.type = "text/javascript"
        script.async = true
        script.innerHTML = JSON.stringify({
            autosize: true,
            symbol: `BINANCE:${symbol}`,
            interval: "15",
            timezone: "Africa/Cairo",
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

        script.onload = () => setIsLoading(false)
        container.appendChild(script)

        return () => {
            if (container) {
                container.innerHTML = ""
            }
        }
    }, [symbol, theme])

    return (
        <div className="tradingview-widget-container relative w-full rounded-lg border border-border bg-card overflow-hidden z-10" style={{ height: "600px" }}>
            {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                    <div className="flex flex-col items-center gap-3">
                        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
                        <span className="text-sm text-gray-400">Loading Chart...</span>
                    </div>
                </div>
            )}
            <div ref={containerRef} className="h-full w-full" />
        </div>
    )
}

