"use client"

import { useState } from "react"
import { Zap } from "lucide-react"
import { useQuantumSocket } from "@/hooks/use-quantum-socket"
import { StatusIndicator } from "@/components/status-indicator"
import { AccountCard } from "@/components/account-card"
import { SignalsCard } from "@/components/signals-card"
import { ConsoleCard } from "@/components/console-card"
import { TradingChart } from "@/components/trading-chart"
import { NeuralTopology } from "@/components/neural-topology"
import { EngineStatusHero } from "@/components/engine-status-hero"
import { EngineControlPanel } from "@/components/engine-control-panel"
import { AlphaLoopCard } from "@/components/alpha-loop-card"
import { VoiceIndicator } from "@/components/voice-indicator"
import { DownloadModal } from "@/components/download-modal"

export default function AlphaAxiomDashboard() {
  const { isConnected, isConnecting, account, signals, logs, connect } = useQuantumSocket()
  const [isDownloadModalOpen, setIsDownloadModalOpen] = useState(false)

  const handleDownload = () => {
    setIsDownloadModalOpen(true)
  }

  const handleSentinel = () => {
    window.open("https://t.me/AlphaAxiomBot", "_blank")
  }

  // Engine state - would come from WebSocket in production
  const engineState = isConnected ? "running" : isConnecting ? "connecting" : "stopped"

  return (
    <div className="min-h-screen bg-background relative">
      {/* Background Neural Network */}
      <NeuralTopology />

      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div
              className="flex h-9 w-9 items-center justify-center rounded-lg"
              style={{ backgroundColor: "rgba(57, 255, 20, 0.1)" }}
            >
              <Zap className="h-5 w-5" style={{ color: "var(--color-neon-green)" }} />
            </div>
            <div>
              <h1 className="text-base font-semibold tracking-tight text-foreground">AlphaAxiom</h1>
              <p className="text-xs text-muted-foreground">Money Machine v1.0</p>
            </div>
          </div>

          <StatusIndicator
            isConnected={isConnected}
            isConnecting={isConnecting}
            onConnect={connect}
            onDownload={handleDownload}
            onSentinel={handleSentinel}
          />
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* NEW: Engine Status Hero */}
        <EngineStatusHero
          engineState={engineState}
          wallet={10000}
          generation={3}
          tradestoday={2}
          maxTrades={10}
        />

        {/* NEW: Control + Alpha Loop + Voice Row */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mb-6">
          <EngineControlPanel
            isRunning={isConnected}
            currentMode="scalping"
            riskLevel="medium"
            autoTrade={false}
            onStart={connect}
          />
          <AlphaLoopCard
            generation={3}
            lastEvolution="Dec 10, 2025"
            nextEvolutionIn="4 days"
          />
          <VoiceIndicator
            isListening={false}
            isConnected={isConnected}
            lastCommand="Start scalping Bitcoin"
            lastCommandTime="2m ago"
          />
        </div>

        {/* TradingView Chart */}
        <div className="mb-6">
          <TradingChart symbol="BTCUSD" theme="dark" />
        </div>

        {/* Data Cards Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <div className="lg:col-span-1">
            <AccountCard account={account} />
          </div>
          <div className="lg:col-span-1">
            <SignalsCard signals={signals} />
          </div>
          <div className="md:col-span-2 lg:col-span-1">
            <ConsoleCard logs={logs} />
          </div>
        </div>

        {/* Footer Stats */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-6 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: "var(--color-neon-green)" }}></span>
            <span>Latency: 12ms</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground"></span>
            <span>API: REST/WSS</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground"></span>
            <span>Engine: oracle.axiomid.app</span>
          </div>
        </div>
      </main>

      {/* Wispr Flow-style Download Modal */}
      <DownloadModal
        isOpen={isDownloadModalOpen}
        onClose={() => setIsDownloadModalOpen(false)}
      />
    </div>
  )
}

