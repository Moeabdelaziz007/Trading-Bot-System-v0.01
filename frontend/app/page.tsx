"use client"

import { Zap } from "lucide-react"
import { useQuantumSocket } from "@/hooks/use-quantum-socket"
import { StatusIndicator } from "@/components/status-indicator"
import { AccountCard } from "@/components/account-card"
import { SignalsCard } from "@/components/signals-card"
import { ConsoleCard } from "@/components/console-card"

export default function QuantumDashboard() {
  const { isConnected, isConnecting, account, signals, logs, connect } = useQuantumSocket()

  const handleDownload = () => {
    window.open("https://github.com/quantum-trading-engine/releases", "_blank")
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#39FF14]/10">
              <Zap className="h-5 w-5 text-[#39FF14]" />
            </div>
            <div>
              <h1 className="text-base font-semibold tracking-tight text-foreground">AlphaQuanTopology</h1>
              <p className="text-xs text-muted-foreground">AQT Neural Engine v2.4</p>
            </div>
          </div>

          <StatusIndicator
            isConnected={isConnected}
            isConnecting={isConnecting}
            onConnect={connect}
            onDownload={handleDownload}
          />
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Connection Error Banner */}
        {!isConnected && !isConnecting && (
          <div className="mb-6 rounded-lg border border-border bg-secondary/30 p-4">
            <p className="text-sm text-muted-foreground">
              <span className="font-medium text-foreground">Engine not running?</span> Download and run the AQT Engine
              locally, then click the status indicator to connect.
            </p>
          </div>
        )}

        {/* Bento Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {/* Account Card - Spans full width on mobile, 1 col on larger */}
          <div className="lg:col-span-1">
            <AccountCard account={account} />
          </div>

          {/* Signals Card */}
          <div className="lg:col-span-1">
            <SignalsCard signals={signals} />
          </div>

          {/* Console Card - Takes remaining space */}
          <div className="md:col-span-2 lg:col-span-1">
            <ConsoleCard logs={logs} />
          </div>
        </div>

        {/* Footer Stats */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-6 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-[#39FF14]"></span>
            <span>Latency: 12ms</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground"></span>
            <span>API: REST/WSS</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground"></span>
            <span>AQT Engine: localhost:8765</span>
          </div>
        </div>
      </main>
    </div>
  )
}
