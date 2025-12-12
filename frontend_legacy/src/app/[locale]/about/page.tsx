"use client";
import { motion } from 'framer-motion';
import {
    Info,
    Cpu,
    Globe,
    Zap,
    ShieldCheck,
    Database,
    Code,
    Github
} from 'lucide-react';
import Link from 'next/link';

export default function AboutPage() {
    return (
        <div className="min-h-screen space-y-8 animate-fade-in p-2 md:p-0 pb-20">
            {/* Hero Section */}
            <div className="text-center space-y-4 py-12 relative overflow-hidden bento-card border-none bg-gradient-to-b from-[var(--navy-deep)] to-[var(--void)]">
                <div className="absolute inset-0 bg-carbon-fiber opacity-30" />
                <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="relative z-10"
                >
                    <h1 className="text-5xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-[var(--neon-cyan)] via-[var(--neon-purple)] to-[var(--neon-magenta)] mb-4 neon-text">
                        AXIOM ANTIGRAVITY
                    </h1>
                    <p className="text-xl text-[var(--text-muted)] max-w-2xl mx-auto font-light">
                        The First Autonomous AI Signal & Trading Infrastructure.
                    </p>
                </motion.div>
            </div>

            {/* Architecture Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

                {/* Engine Card */}
                <motion.div whileHover={{ y: -5 }} className="bento-card p-6 border-t-4 border-t-[var(--neon-cyan)]">
                    <Cpu className="w-10 h-10 text-[var(--neon-cyan)] mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">Twin-Turbo Engines</h3>
                    <p className="text-sm text-[var(--text-dim)]">
                        Powered by <span className="text-white">AEXI</span> (Exhaustion & Velocity) and <span className="text-white">Dream Machine</span> (Fractal & Entropy) algorithms for high-precision signal detection.
                    </p>
                </motion.div>

                {/* AI Card */}
                <motion.div whileHover={{ y: -5 }} className="bento-card p-6 border-t-4 border-t-[var(--neon-purple)]">
                    <Zap className="w-10 h-10 text-[var(--neon-purple)] mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">Spider Agents</h3>
                    <p className="text-sm text-[var(--text-dim)]">
                        Modular AI swarm including <span className="text-white">Analyst</span>, <span className="text-white">Reflex</span>, and <span className="text-white">Guardian</span> working in harmony.
                    </p>
                </motion.div>

                {/* Infrastructure Card */}
                <motion.div whileHover={{ y: -5 }} className="bento-card p-6 border-t-4 border-t-[var(--neon-green)]">
                    <Globe className="w-10 h-10 text-[var(--neon-green)] mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">Zero-Cost Infra</h3>
                    <p className="text-sm text-[var(--text-dim)]">
                        Deployed on Cloudflare Workers (Edge), D1 Database, and Vercel for maximum speed and zero operational cost.
                    </p>
                </motion.div>
            </div>

            {/* Tech Stack List */}
            <div className="bento-card p-8">
                <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                    <Code className="w-6 h-6 text-[var(--neon-magenta)]" />
                    Technical Stack
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {['Next.js 14', 'TypeScript', 'Tailwind CSS', 'Framer Motion', 'Cloudflare Workers', 'Python (Pyodide)', 'Z.ai GLM-4.5', 'Groq API'].map((tech) => (
                        <div key={tech} className="p-3 bg-[var(--surface)] border border-[var(--glass-border)] rounded-lg text-center text-sm font-mono text-[var(--text-muted)] hover:border-[var(--neon-cyan)] transition-colors">
                            {tech}
                        </div>
                    ))}
                </div>
            </div>

            {/* CTA */}
            <div className="text-center">
                <Link
                    href="https://github.com/Moeabdelaziz007/Trading-Bot-System-v0.01"
                    target="_blank"
                    className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-[var(--neon-purple)] to-[var(--neon-magenta)] text-white font-bold text-lg hover:shadow-[0_0_30px_rgba(236,72,153,0.4)] transition-all"
                >
                    <Github className="w-5 h-5" /> View Source on GitHub
                </Link>
                <p className="mt-4 text-xs text-[var(--text-dim)]">
                    v0.9.2-beta • Licensed under MIT
                </p>
            </div>
        </div>
    );
}
