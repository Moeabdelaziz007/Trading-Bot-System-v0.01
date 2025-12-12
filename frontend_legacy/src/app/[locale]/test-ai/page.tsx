"use client";
import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Terminal,
    Send,
    Cpu,
    ShieldAlert,
    Zap,
    Activity,
    Play,
    RotateCcw,
    Code2
} from 'lucide-react';

export default function TestAIPage() {
    const [prompt, setPrompt] = useState('Analyze EURUSD for a potential LONG position on H1 timeframe. Current price 1.0850.');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [terminalLines, setTerminalLines] = useState<string[]>(['> Axis Antigravity AI Link Established...', '> Ready for simulation.']);

    const addLog = (text: string) => {
        setTerminalLines(prev => [...prev.slice(-10), `> ${text}`]);
    };

    const handleSimulate = async () => {
        if (!prompt.trim()) return;
        setLoading(true);
        setResult(null);
        addLog(`Analyzing: "${prompt.substring(0, 30)}..."`);

        try {
            const res = await fetch('/api/test-ai', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, model: 'GLM-4.5' })
            });
            const data = await res.json();

            if (data.success) {
                setResult(data);
                addLog('Analysis Complete. Metrics received.');
            } else {
                addLog('Error: Simulation failed.');
            }
        } catch (e) {
            addLog('System Error: Connection Refused.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen space-y-6 animate-fade-in p-2 md:p-0">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[var(--neon-cyan)] to-[var(--neon-purple)] flex items-center gap-3">
                        <Terminal className="w-8 h-8 text-[var(--neon-cyan)]" />
                        AI Strategy Simulator
                    </h1>
                    <p className="text-sm text-[var(--text-muted)] mt-1 font-mono">
                        Powered by Z.ai GLM-4.5 • Simulation Mode • Zero Risk
                    </p>
                </div>
                <div className="hidden md:flex items-center gap-2">
                    <span className="px-3 py-1 rounded-full bg-[var(--neon-purple)]/10 text-[var(--neon-purple)] text-xs font-mono border border-[var(--neon-purple)]/50">
                        TESTNET ACTIVE
                    </span>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Panel: Controls */}
                <div className="lg:col-span-2 space-y-6">

                    {/* Input Area */}
                    <div className="bento-card p-6 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-50">
                            <Cpu className="w-24 h-24 text-[var(--neon-cyan)]/10 rotate-12" />
                        </div>

                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Code2 className="w-5 h-5 text-[var(--neon-cyan)]" />
                            Simulation Parameters
                        </h2>

                        <div className="space-y-4">
                            <div>
                                <label className="text-xs text-[var(--text-dim)] uppercase mb-2 block">Instruction Prompt</label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    className="w-full h-32 bg-[var(--void)] border border-[var(--glass-border)] rounded-xl p-4 text-sm font-mono text-white focus:border-[var(--neon-cyan)] focus:ring-1 focus:ring-[var(--neon-cyan)] transition-all resize-none"
                                    placeholder="Enter your strategy instructions here..."
                                />
                            </div>

                            <div className="flex gap-4">
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={handleSimulate}
                                    disabled={loading}
                                    className={`flex-1 py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${loading
                                        ? 'bg-[var(--glass-border)] text-[var(--text-dim)] cursor-not-allowed'
                                        : 'bg-gradient-to-r from-[var(--neon-cyan)] to-[var(--neon-blue)] text-black shadow-[0_0_20px_rgba(0,240,255,0.3)] hover:shadow-[0_0_30px_rgba(0,240,255,0.5)]'
                                        }`}
                                >
                                    {loading ? <RotateCcw className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
                                    {loading ? 'Processing Simulation...' : 'Run Simulation'}
                                </motion.button>
                            </div>
                        </div>
                    </div>

                    {/* Output Log Terminal */}
                    <div className="bento-card p-0 overflow-hidden flex flex-col h-[300px]">
                        <div className="bg-[var(--void)]/50 p-3 border-b border-[var(--glass-border)] flex items-center gap-2">
                            <div className="flex gap-1.5">
                                <div className="w-3 h-3 rounded-full bg-red-500/50" />
                                <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
                                <div className="w-3 h-3 rounded-full bg-green-500/50" />
                            </div>
                            <span className="text-xs font-mono text-[var(--text-dim)] ml-2">system_log.txt</span>
                        </div>
                        <div className="flex-1 bg-black/50 p-4 font-mono text-xs text-[var(--neon-green)] overflow-y-auto font-bold">
                            {terminalLines.map((line, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    className="mb-1"
                                >
                                    {line}
                                </motion.div>
                            ))}
                            {loading && (
                                <div className="animate-pulse">_</div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Right Panel: Analysis Result */}
                <div className="bento-card p-6 h-full border-l-4 border-l-[var(--neon-purple)]">
                    <h2 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                        <Zap className="w-5 h-5 text-[var(--neon-purple)]" />
                        AI Analysis Result
                    </h2>

                    <AnimatePresence mode="wait">
                        {result ? (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="space-y-6"
                            >
                                {/* Confidence Score */}
                                <div className="p-4 rounded-xl bg-[var(--void)] border border-[var(--glass-border)]">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-xs text-[var(--text-dim)] uppercase">Confidence</span>
                                        <span className="text-xl font-bold text-[var(--neon-cyan)]">{result.metrics.confidence}%</span>
                                    </div>
                                    <div className="h-2 w-full bg-[var(--surface)] rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${result.metrics.confidence}%` }}
                                            transition={{ duration: 1 }}
                                            className="h-full bg-gradient-to-r from-[var(--neon-cyan)] to-[var(--neon-blue)]"
                                        />
                                    </div>
                                </div>

                                {/* Markdown Content */}
                                <div className="prose prose-invert prose-sm max-w-none">
                                    <div className="text-sm text-[var(--text-muted)] whitespace-pre-line leading-relaxed border-l-2 border-[var(--glass-border)] pl-4">
                                        {result.analysis}
                                    </div>
                                </div>

                                {/* Action Advice */}
                                <div className={`p-4 rounded-xl flex items-center gap-3 ${result.metrics.risk_level === 'High'
                                    ? 'bg-red-500/10 border border-red-500/30'
                                    : 'bg-green-500/10 border border-green-500/30'
                                    }`}>
                                    <ShieldAlert className={`w-6 h-6 ${result.metrics.risk_level === 'High' ? 'text-red-500' : 'text-green-500'
                                        }`} />
                                    <div>
                                        <p className="text-xs uppercase opacity-70">Risk Level</p>
                                        <p className="font-bold">{result.metrics.risk_level}</p>
                                    </div>
                                </div>
                            </motion.div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-[var(--text-dim)] opacity-50">
                                <Activity className="w-16 h-16 mb-4 animate-pulse" />
                                <p>Waiting for simulation...</p>
                            </div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
}
