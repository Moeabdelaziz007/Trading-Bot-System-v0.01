"use client"

import { motion } from "framer-motion"
import { Activity, Zap, TrendingUp, Brain } from "lucide-react"

interface EngineStatusHeroProps {
    engineState: "running" | "stopped" | "connecting"
    wallet: number
    generation: number
    tradestoday?: number
    maxTrades?: number
}

export function EngineStatusHero({
    engineState = "stopped",
    wallet = 10000,
    generation = 0,
    tradestoday = 0,
    maxTrades = 10,
}: EngineStatusHeroProps) {
    const stateConfig = {
        running: {
            color: "var(--color-neon-green)",
            bg: "rgba(57, 255, 20, 0.1)",
            label: "LIVE",
            pulse: true,
        },
        stopped: {
            color: "#FF3366",
            bg: "rgba(255, 51, 102, 0.1)",
            label: "OFFLINE",
            pulse: false,
        },
        connecting: {
            color: "#F59E0B",
            bg: "rgba(245, 158, 11, 0.1)",
            label: "CONNECTING",
            pulse: true,
        },
    }

    const config = stateConfig[engineState]

    return (
        <div className="relative overflow-hidden rounded-xl border border-border bg-card/50 backdrop-blur-xl p-6 mb-6">
            {/* Animated Background Gradient */}
            <div
                className="absolute inset-0 opacity-20"
                style={{
                    background: `radial-gradient(circle at 30% 50%, ${config.bg} 0%, transparent 50%)`,
                }}
            />

            <div className="relative flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                {/* Left: Status & Brand */}
                <div className="flex items-center gap-4">
                    {/* Animated Status Orb */}
                    <motion.div
                        className="relative flex h-16 w-16 items-center justify-center rounded-full"
                        style={{ backgroundColor: config.bg }}
                        animate={config.pulse ? { scale: [1, 1.05, 1] } : {}}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        <Zap className="h-8 w-8" style={{ color: config.color }} />
                        {config.pulse && (
                            <motion.div
                                className="absolute inset-0 rounded-full"
                                style={{ border: `2px solid ${config.color}` }}
                                animate={{ scale: [1, 1.5], opacity: [0.8, 0] }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                            />
                        )}
                    </motion.div>

                    <div>
                        <div className="flex items-center gap-2">
                            <h2 className="text-2xl font-bold text-foreground">AlphaAxiom</h2>
                            <span
                                className="px-2 py-0.5 rounded-full text-xs font-semibold"
                                style={{ backgroundColor: config.bg, color: config.color }}
                            >
                                {config.label}
                            </span>
                        </div>
                        <p className="text-sm text-muted-foreground">Money Machine Engine v1.0</p>
                    </div>
                </div>

                {/* Right: Stats Grid */}
                <div className="grid grid-cols-3 gap-6">
                    {/* Wallet */}
                    <div className="text-center">
                        <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
                            <TrendingUp className="h-3 w-3" />
                            <span className="text-xs">Wallet</span>
                        </div>
                        <p className="text-xl font-bold text-foreground">
                            ${wallet.toLocaleString()}
                        </p>
                    </div>

                    {/* Generation */}
                    <div className="text-center">
                        <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
                            <Brain className="h-3 w-3" />
                            <span className="text-xs">Generation</span>
                        </div>
                        <p className="text-xl font-bold" style={{ color: "var(--color-neon-green)" }}>
                            Gen {generation}
                        </p>
                    </div>

                    {/* Trades Today */}
                    <div className="text-center">
                        <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
                            <Activity className="h-3 w-3" />
                            <span className="text-xs">Trades</span>
                        </div>
                        <p className="text-xl font-bold text-foreground">
                            {tradestoday}/{maxTrades}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}
