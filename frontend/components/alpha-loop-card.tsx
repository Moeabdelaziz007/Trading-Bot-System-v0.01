"use client"

import { motion } from "framer-motion"
import { Brain, Clock, TrendingUp } from "lucide-react"

interface StrategyWeight {
    name: string
    weight: number
    winRate: number
}

interface AlphaLoopCardProps {
    generation?: number
    lastEvolution?: string
    nextEvolutionIn?: string
    strategies?: StrategyWeight[]
}

export function AlphaLoopCard({
    generation = 0,
    lastEvolution = "Never",
    nextEvolutionIn = "7 days",
    strategies = [
        { name: "Cipher", weight: 25, winRate: 55 },
        { name: "News", weight: 25, winRate: 48 },
        { name: "Momentum", weight: 25, winRate: 52 },
        { name: "Reversal", weight: 25, winRate: 50 },
    ],
}: AlphaLoopCardProps) {
    return (
        <div className="rounded-xl border border-border bg-card/50 backdrop-blur-xl p-4 h-full">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <div
                        className="flex h-8 w-8 items-center justify-center rounded-lg"
                        style={{ backgroundColor: "rgba(168, 85, 247, 0.1)" }}
                    >
                        <Brain className="h-4 w-4" style={{ color: "#A855F7" }} />
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-foreground">Alpha Loop</h3>
                        <p className="text-xs text-muted-foreground">Self-Learning Engine</p>
                    </div>
                </div>
                <div
                    className="px-2 py-1 rounded-full text-xs font-bold"
                    style={{ backgroundColor: "rgba(168, 85, 247, 0.1)", color: "#A855F7" }}
                >
                    Gen {generation}
                </div>
            </div>

            {/* Evolution Timeline */}
            <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="p-2 rounded-lg bg-secondary/30">
                    <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
                        <Clock className="h-3 w-3" />
                        <span>Last Evolution</span>
                    </div>
                    <p className="text-sm font-medium text-foreground">{lastEvolution}</p>
                </div>
                <div className="p-2 rounded-lg bg-secondary/30">
                    <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
                        <TrendingUp className="h-3 w-3" />
                        <span>Next In</span>
                    </div>
                    <p className="text-sm font-medium text-foreground">{nextEvolutionIn}</p>
                </div>
            </div>

            {/* Strategy Weights */}
            <div>
                <p className="text-xs text-muted-foreground mb-2">Strategy Weights</p>
                <div className="space-y-2">
                    {strategies.map((strategy) => (
                        <div key={strategy.name} className="flex items-center gap-2">
                            <span className="text-xs text-foreground w-16">{strategy.name}</span>
                            <div className="flex-1 h-2 bg-secondary/50 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full rounded-full"
                                    style={{ backgroundColor: "var(--color-neon-green)" }}
                                    initial={{ width: 0 }}
                                    animate={{ width: `${strategy.weight}%` }}
                                    transition={{ duration: 0.8, delay: 0.1 }}
                                />
                            </div>
                            <span className="text-xs text-muted-foreground w-12 text-right">
                                {strategy.weight}%
                            </span>
                            <span
                                className="text-xs w-10 text-right"
                                style={{ color: strategy.winRate >= 50 ? "#10B981" : "#EF4444" }}
                            >
                                {strategy.winRate}%
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
