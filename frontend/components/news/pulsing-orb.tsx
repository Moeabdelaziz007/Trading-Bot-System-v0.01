"use client";

import { motion } from "framer-motion";
import { Activity } from "lucide-react";

interface PulsingOrbProps {
    state?: "idle" | "analyzing" | "alert";
}

const PulsingOrb = ({ state = "idle" }: PulsingOrbProps) => {
    const stateStyles = {
        idle: {
            gradient: "linear-gradient(135deg, #06b6d4 0%, #2563eb 100%)",
            shadow: "var(--glow-primary)"
        },
        analyzing: {
            gradient: "linear-gradient(135deg, #a855f7 0%, #ec4899 100%)",
            shadow: "0 0 20px rgba(168, 85, 247, 0.4)"
        },
        alert: {
            gradient: "linear-gradient(135deg, #ef4444 0%, #f97316 100%)",
            shadow: "var(--glow-bearish)"
        }
    };

    return (
        <div className="relative">
            <motion.div
                className="w-12 h-12 rounded-full shadow-lg"
                style={{
                    background: stateStyles[state].gradient,
                    boxShadow: stateStyles[state].shadow
                }}
                animate={{
                    scale: [1, 1.15, 1],
                    boxShadow: [
                        stateStyles[state].shadow,
                        state === "idle" ? "var(--glow-primary-strong)" : 
                        state === "analyzing" ? "0 0 40px rgba(168, 85, 247, 0.6)" :
                        "var(--glow-bearish-strong)",
                        stateStyles[state].shadow
                    ]
                }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            >
                <div className="absolute inset-0 flex items-center justify-center">
                    <Activity className="w-5 h-5 text-white/80" />
                </div>
            </motion.div>
            {/* Outer ring */}
            <motion.div
                className="absolute inset-0 rounded-full border-2"
                style={{ borderColor: "var(--color-primary-cyan)", opacity: 0.3 }}
                animate={{ scale: [1, 1.5], opacity: [0.6, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
            />
        </div>
    );
};

export default PulsingOrb;