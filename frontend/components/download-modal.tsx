"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
    Download,
    Check,
    Zap,
    Mic,
    Shield,
    Sparkles,
    Apple,
    Monitor,
    ChevronRight,
    X
} from "lucide-react"

interface DownloadModalProps {
    isOpen: boolean
    onClose: () => void
}

export function DownloadModal({ isOpen, onClose }: DownloadModalProps) {
    const [step, setStep] = useState<"choose" | "downloading" | "ready">("choose")
    const [progress, setProgress] = useState(0)
    const [selectedPlatform, setSelectedPlatform] = useState<"mac" | "windows" | null>(null)

    const handleDownload = (platform: "mac" | "windows") => {
        setSelectedPlatform(platform)
        setStep("downloading")

        // Simulate download progress
        let prog = 0
        const interval = setInterval(() => {
            prog += Math.random() * 15
            if (prog >= 100) {
                prog = 100
                clearInterval(interval)
                setTimeout(() => setStep("ready"), 500)
            }
            setProgress(prog)
        }, 200)

        // Trigger actual download
        const link = document.createElement('a')
        link.href = platform === "mac" ? "/AlphaAxiom-Mac.dmg" : "/AlphaReceiver.mq5"
        link.download = platform === "mac" ? "AlphaAxiom-Mac.dmg" : "AlphaReceiver.mq5"
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }

    const features = [
        { icon: Zap, text: "4x faster trading decisions" },
        { icon: Mic, text: "Voice-controlled execution" },
        { icon: Shield, text: "Aladdin-grade risk shield" },
        { icon: Sparkles, text: "Self-learning AI engine" },
    ]

    const setupSteps = [
        "Extract AlphaAxiom to your folder",
        "Add to MT5: File → Open Data Folder → MQL5/Experts",
        "Restart MetaTrader 5",
        "Attach to chart and enable AutoTrading",
    ]

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
                    onClick={onClose}
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        transition={{ type: "spring", damping: 25, stiffness: 300 }}
                        onClick={(e) => e.stopPropagation()}
                        className="relative w-full max-w-lg rounded-2xl border border-white/10 bg-gradient-to-b from-zinc-900 to-black overflow-hidden"
                    >
                        {/* Close Button */}
                        <button
                            onClick={onClose}
                            className="absolute top-4 right-4 p-2 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
                        >
                            <X className="h-4 w-4 text-white/60" />
                        </button>

                        {/* Step: Choose Platform */}
                        <AnimatePresence mode="wait">
                            {step === "choose" && (
                                <motion.div
                                    key="choose"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    className="p-8"
                                >
                                    {/* Header */}
                                    <div className="text-center mb-8">
                                        <motion.div
                                            className="inline-flex h-16 w-16 items-center justify-center rounded-2xl mb-4"
                                            style={{ backgroundColor: "rgba(57, 255, 20, 0.1)" }}
                                            animate={{ scale: [1, 1.05, 1] }}
                                            transition={{ duration: 2, repeat: Infinity }}
                                        >
                                            <Zap className="h-8 w-8" style={{ color: "#39FF14" }} />
                                        </motion.div>
                                        <h2 className="text-2xl font-bold text-white mb-2">
                                            Download AlphaAxiom
                                        </h2>
                                        <p className="text-sm text-white/60">
                                            The Money Machine for your trading terminal
                                        </p>
                                    </div>

                                    {/* Platform Buttons */}
                                    <div className="grid grid-cols-2 gap-4 mb-8">
                                        <motion.button
                                            onClick={() => handleDownload("mac")}
                                            className="flex flex-col items-center gap-3 p-6 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-all"
                                            whileHover={{ scale: 1.02, y: -2 }}
                                            whileTap={{ scale: 0.98 }}
                                        >
                                            <Apple className="h-8 w-8 text-white" />
                                            <span className="text-sm font-medium text-white">macOS</span>
                                            <span className="text-xs text-white/40">Intel & Apple Silicon</span>
                                        </motion.button>
                                        <motion.button
                                            onClick={() => handleDownload("windows")}
                                            className="flex flex-col items-center gap-3 p-6 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-all"
                                            whileHover={{ scale: 1.02, y: -2 }}
                                            whileTap={{ scale: 0.98 }}
                                        >
                                            <Monitor className="h-8 w-8 text-white" />
                                            <span className="text-sm font-medium text-white">Windows</span>
                                            <span className="text-xs text-white/40">MetaTrader 5 EA</span>
                                        </motion.button>
                                    </div>

                                    {/* Features */}
                                    <div className="grid grid-cols-2 gap-3">
                                        {features.map((feature, i) => (
                                            <motion.div
                                                key={i}
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                transition={{ delay: 0.1 * i }}
                                                className="flex items-center gap-2 text-sm text-white/60"
                                            >
                                                <feature.icon className="h-4 w-4" style={{ color: "#39FF14" }} />
                                                <span>{feature.text}</span>
                                            </motion.div>
                                        ))}
                                    </div>
                                </motion.div>
                            )}

                            {/* Step: Downloading */}
                            {step === "downloading" && (
                                <motion.div
                                    key="downloading"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    className="p-8"
                                >
                                    <div className="text-center mb-8">
                                        <motion.div
                                            className="inline-flex h-16 w-16 items-center justify-center rounded-2xl mb-4"
                                            style={{ backgroundColor: "rgba(57, 255, 20, 0.1)" }}
                                            animate={{ rotate: 360 }}
                                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                        >
                                            <Download className="h-8 w-8" style={{ color: "#39FF14" }} />
                                        </motion.div>
                                        <h2 className="text-2xl font-bold text-white mb-2">
                                            Downloading...
                                        </h2>
                                        <p className="text-sm text-white/60">
                                            {selectedPlatform === "mac" ? "AlphaAxiom-Mac.dmg" : "AlphaReceiver.mq5"}
                                        </p>
                                    </div>

                                    {/* Progress Bar */}
                                    <div className="mb-4">
                                        <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                                            <motion.div
                                                className="h-full rounded-full"
                                                style={{
                                                    backgroundColor: "#39FF14",
                                                    width: `${progress}%`
                                                }}
                                                initial={{ width: 0 }}
                                            />
                                        </div>
                                        <p className="text-center text-sm text-white/40 mt-2">
                                            {Math.round(progress)}%
                                        </p>
                                    </div>
                                </motion.div>
                            )}

                            {/* Step: Ready */}
                            {step === "ready" && (
                                <motion.div
                                    key="ready"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    className="p-8"
                                >
                                    <div className="text-center mb-6">
                                        <motion.div
                                            className="inline-flex h-16 w-16 items-center justify-center rounded-2xl mb-4"
                                            style={{ backgroundColor: "rgba(57, 255, 20, 0.2)" }}
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            transition={{ type: "spring", damping: 10 }}
                                        >
                                            <Check className="h-8 w-8" style={{ color: "#39FF14" }} />
                                        </motion.div>
                                        <h2 className="text-2xl font-bold text-white mb-2">
                                            Download Complete!
                                        </h2>
                                        <p className="text-sm text-white/60">
                                            Follow these steps to get started
                                        </p>
                                    </div>

                                    {/* Setup Steps */}
                                    <div className="space-y-3 mb-6">
                                        {setupSteps.map((stepText, i) => (
                                            <motion.div
                                                key={i}
                                                initial={{ opacity: 0, x: -20 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: 0.1 * i }}
                                                className="flex items-start gap-3 p-3 rounded-lg bg-white/5"
                                            >
                                                <div
                                                    className="flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold"
                                                    style={{ backgroundColor: "rgba(57, 255, 20, 0.2)", color: "#39FF14" }}
                                                >
                                                    {i + 1}
                                                </div>
                                                <p className="text-sm text-white/80 pt-0.5">{stepText}</p>
                                            </motion.div>
                                        ))}
                                    </div>

                                    {/* CTA Buttons */}
                                    <div className="flex gap-3">
                                        <motion.button
                                            onClick={onClose}
                                            className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-medium text-sm"
                                            style={{
                                                backgroundColor: "#39FF14",
                                                color: "#000"
                                            }}
                                            whileHover={{ scale: 1.02 }}
                                            whileTap={{ scale: 0.98 }}
                                        >
                                            Start Trading
                                            <ChevronRight className="h-4 w-4" />
                                        </motion.button>
                                        <motion.button
                                            onClick={() => window.open("https://t.me/AlphaAxiomBot", "_blank")}
                                            className="px-4 py-3 rounded-xl font-medium text-sm border border-white/20 text-white hover:bg-white/5"
                                            whileHover={{ scale: 1.02 }}
                                            whileTap={{ scale: 0.98 }}
                                        >
                                            Join Telegram
                                        </motion.button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    )
}
