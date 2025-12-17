"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Power, Settings, Zap, Shield, TrendingUp } from "lucide-react"

interface EngineControlPanelProps {
    isRunning?: boolean
    currentMode?: "scalping" | "swing" | "sniper"
    riskLevel?: "low" | "medium" | "high"
    autoTrade?: boolean
    onStart?: () => void
    onStop?: () => void
    onModeChange?: (mode: string) => void
    onRiskChange?: (risk: string) => void
}

export function EngineControlPanel({
    isRunning = false,
    currentMode = "scalping",
    riskLevel = "medium",
    autoTrade = false,
    onStart,
    onStop,
    onModeChange,
    onRiskChange,
}: EngineControlPanelProps) {
    const [selectedMode, setSelectedMode] = useState(currentMode)
    const [selectedRisk, setSelectedRisk] = useState(riskLevel)

    const modes = [
        { id: "scalping", label: "Scalping", icon: Zap },
        { id: "swing", label: "Swing", icon: TrendingUp },
        { id: "sniper", label: "Sniper", icon: Shield },
    ]

    const risks = [
        { id: "low", label: "Conservative", color: "#10B981" },
        { id: "medium", label: "Balanced", color: "#F59E0B" },
        { id: "high", label: "Aggressive", color: "#EF4444" },
    ]

    const handleModeClick = (mode: string) => {
        setSelectedMode(mode as typeof currentMode)
        onModeChange?.(mode)
    }

    const handleRiskClick = (risk: string) => {
        setSelectedRisk(risk as typeof riskLevel)
        onRiskChange?.(risk)
    }

    return (
        <div className="rounded-xl border border-border bg-card/50 backdrop-blur-xl p-4">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Settings className="h-4 w-4 text-muted-foreground" />
                    <h3 className="text-sm font-semibold text-foreground">Engine Control</h3>
                </div>

                {/* Power Button */}
                <motion.button
                    onClick={isRunning ? onStop : onStart}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all"
                    style={{
                        backgroundColor: isRunning ? "rgba(239, 68, 68, 0.1)" : "rgba(57, 255, 20, 0.1)",
                        color: isRunning ? "#EF4444" : "var(--color-neon-green)",
                        border: `1px solid ${isRunning ? "rgba(239, 68, 68, 0.3)" : "rgba(57, 255, 20, 0.3)"}`,
                    }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <Power className="h-4 w-4" />
                    {isRunning ? "Stop" : "Start"}
                </motion.button>
            </div>

            {/* Mode Selector */}
            <div className="mb-4">
                <p className="text-xs text-muted-foreground mb-2">Trading Mode</p>
                <div className="flex gap-2">
                    {modes.map((mode) => {
                        const Icon = mode.icon
                        const isActive = selectedMode === mode.id
                        return (
                            <button
                                key={mode.id}
                                onClick={() => handleModeClick(mode.id)}
                                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all"
                                style={{
                                    backgroundColor: isActive ? "rgba(57, 255, 20, 0.1)" : "rgba(255, 255, 255, 0.02)",
                                    color: isActive ? "var(--color-neon-green)" : "var(--muted-foreground)",
                                    border: `1px solid ${isActive ? "rgba(57, 255, 20, 0.3)" : "rgba(255, 255, 255, 0.05)"}`,
                                }}
                            >
                                <Icon className="h-3 w-3" />
                                {mode.label}
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* Risk Level */}
            <div>
                <p className="text-xs text-muted-foreground mb-2">Risk Level</p>
                <div className="flex gap-2">
                    {risks.map((risk) => {
                        const isActive = selectedRisk === risk.id
                        return (
                            <button
                                key={risk.id}
                                onClick={() => handleRiskClick(risk.id)}
                                className="flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all"
                                style={{
                                    backgroundColor: isActive ? `${risk.color}15` : "rgba(255, 255, 255, 0.02)",
                                    color: isActive ? risk.color : "var(--muted-foreground)",
                                    border: `1px solid ${isActive ? `${risk.color}40` : "rgba(255, 255, 255, 0.05)"}`,
                                }}
                            >
                                {risk.label}
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* Auto Trade Warning */}
            {!autoTrade && (
                <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground p-2 rounded bg-secondary/30">
                    <Shield className="h-3 w-3" />
                    <span>Auto-trade disabled. Signals logged only.</span>
                </div>
            )}
        </div>
    )
}
