"use client"

import { motion } from "framer-motion"
import { Mic, MicOff, Volume2 } from "lucide-react"

interface VoiceIndicatorProps {
    isListening?: boolean
    isConnected?: boolean
    lastCommand?: string
    lastCommandTime?: string
}

export function VoiceIndicator({
    isListening = false,
    isConnected = false,
    lastCommand = "",
    lastCommandTime = "",
}: VoiceIndicatorProps) {
    return (
        <div className="rounded-xl border border-border bg-card/50 backdrop-blur-xl p-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    <motion.div
                        className="flex h-8 w-8 items-center justify-center rounded-full"
                        style={{
                            backgroundColor: isListening
                                ? "rgba(57, 255, 20, 0.2)"
                                : isConnected
                                    ? "rgba(245, 158, 11, 0.1)"
                                    : "rgba(239, 68, 68, 0.1)",
                        }}
                        animate={isListening ? { scale: [1, 1.1, 1] } : {}}
                        transition={{ duration: 1, repeat: Infinity }}
                    >
                        {isListening ? (
                            <Mic className="h-4 w-4" style={{ color: "var(--color-neon-green)" }} />
                        ) : (
                            <MicOff className="h-4 w-4" style={{ color: isConnected ? "#F59E0B" : "#EF4444" }} />
                        )}
                    </motion.div>
                    <div>
                        <h3 className="text-sm font-semibold text-foreground">Voice Control</h3>
                        <p className="text-xs text-muted-foreground">
                            {isListening ? "Listening..." : isConnected ? "Ready" : "Disconnected"}
                        </p>
                    </div>
                </div>

                {/* Status Badge */}
                <div
                    className="px-2 py-1 rounded-full text-xs font-medium"
                    style={{
                        backgroundColor: isListening
                            ? "rgba(57, 255, 20, 0.1)"
                            : isConnected
                                ? "rgba(245, 158, 11, 0.1)"
                                : "rgba(239, 68, 68, 0.1)",
                        color: isListening ? "var(--color-neon-green)" : isConnected ? "#F59E0B" : "#EF4444",
                    }}
                >
                    {isListening ? "● LIVE" : isConnected ? "STANDBY" : "OFFLINE"}
                </div>
            </div>

            {/* Audio Visualizer (when listening) */}
            {isListening && (
                <div className="flex items-center justify-center gap-1 h-8 mb-3">
                    {[...Array(12)].map((_, i) => (
                        <motion.div
                            key={i}
                            className="w-1 rounded-full"
                            style={{ backgroundColor: "var(--color-neon-green)" }}
                            animate={{
                                height: [4, Math.random() * 20 + 8, 4],
                            }}
                            transition={{
                                duration: 0.5,
                                repeat: Infinity,
                                delay: i * 0.05,
                            }}
                        />
                    ))}
                </div>
            )}

            {/* Last Command */}
            {lastCommand && (
                <div className="p-2 rounded-lg bg-secondary/30">
                    <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
                        <Volume2 className="h-3 w-3" />
                        <span>Last Command</span>
                        {lastCommandTime && (
                            <span className="ml-auto text-xs">{lastCommandTime}</span>
                        )}
                    </div>
                    <p className="text-sm text-foreground">&ldquo;{lastCommand}&rdquo;</p>
                </div>
            )}

            {/* Instructions */}
            {!lastCommand && !isListening && (
                <div className="text-xs text-muted-foreground text-center p-2">
                    Hold <kbd className="px-1 py-0.5 bg-secondary rounded text-xs">SPACE</kbd> to speak
                </div>
            )}
        </div>
    )
}
