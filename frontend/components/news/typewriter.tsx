"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";

interface TypewriterProps {
    text: string;
    speed?: number;
}

const Typewriter = ({ text, speed = 30 }: TypewriterProps) => {
    const [displayText, setDisplayText] = useState("");
    const [isComplete, setIsComplete] = useState(false);

    useEffect(() => {
        setDisplayText("");
        setIsComplete(false);
        let i = 0;
        const interval = setInterval(() => {
            if (i < text.length) {
                setDisplayText(text.slice(0, i + 1));
                i++;
            } else {
                setIsComplete(true);
                clearInterval(interval);
            }
        }, speed);
        return () => clearInterval(interval);
    }, [text, speed]);

    return (
        <span>
            {displayText}
            {!isComplete && (
                <motion.span
                    className="inline-block w-2 h-5 ml-1"
                    style={{ backgroundColor: "var(--color-primary-cyan)" }}
                    animate={{ opacity: [1, 0] }}
                    transition={{ duration: 0.5, repeat: Infinity }}
                />
            )}
        </span>
    );
};

export default Typewriter;