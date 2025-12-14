"use client";

import { motion } from "framer-motion";

interface NeonTagProps {
    children: string;
    type?: "critical" | "warning" | "positive" | "neutral";
}

const NeonTag = ({ children, type = "neutral" }: NeonTagProps) => {
    const typeColors = {
        critical: { bg: "rgba(239, 68, 68, 0.2)", border: "rgba(239, 68, 68, 0.5)", text: "#f87171" },
        warning: { bg: "rgba(234, 179, 8, 0.2)", border: "rgba(234, 179, 8, 0.5)", text: "#facc15" },
        positive: { bg: "rgba(34, 197, 94, 0.2)", border: "rgba(34, 197, 94, 0.5)", text: "#4ade80" },
        neutral: { bg: "rgba(156, 163, 175, 0.2)", border: "rgba(156, 163, 175, 0.5)", text: "#9ca3af" }
    };

    const colors = typeColors[type];

    return (
        <motion.span
            className="px-3 py-1 text-xs font-mono uppercase tracking-wider rounded-full border shadow-lg"
            style={{
                backgroundColor: colors.bg,
                borderColor: colors.border,
                color: colors.text
            }}
            whileHover={{ scale: 1.05, boxShadow: `0 0 20px ${colors.text}` }}
        >
            {children}
        </motion.span>
    );
};

export default NeonTag;