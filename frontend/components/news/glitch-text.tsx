"use client";

import { motion } from "framer-motion";

interface GlitchTextProps {
    children: string;
    className?: string;
}

const GlitchText = ({ children, className = "" }: GlitchTextProps) => {
    return (
        <div className={`relative font-mono font-bold ${className}`}>
            <span className="relative z-10">{children}</span>
            <motion.span
                className="absolute top-0 left-0 opacity-80 z-0"
                style={{ color: "var(--color-primary-cyan)" }}
                animate={{ x: [-2, 2, -2], opacity: [0.8, 0.4, 0.8] }}
                transition={{ duration: 0.3, repeat: Infinity, repeatDelay: 3 }}
            >
                {children}
            </motion.span>
            <motion.span
                className="absolute top-0 left-0 opacity-60 z-0"
                style={{ color: "var(--color-sentiment-bearish)" }}
                animate={{ x: [2, -2, 2], opacity: [0.6, 0.3, 0.6] }}
                transition={{ duration: 0.3, repeat: Infinity, repeatDelay: 3.1 }}
            >
                {children}
            </motion.span>
        </div>
    );
};

export default GlitchText;