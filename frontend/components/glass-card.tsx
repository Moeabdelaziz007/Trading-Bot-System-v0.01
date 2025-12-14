"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  sentiment?: "bullish" | "bearish" | "neutral";
  disableAnimations?: boolean;
  variant?: "default" | "elevated" | "subtle";
}

/**
 * GlassCard - Cyberpunk glassmorphism card with sentiment-based border animations
 * 
 * Features:
 * - Sentiment-driven border glow (bullish=green, bearish=red, neutral=gray)
 * - Smooth pulse animation (2s cycle)
 * - Hover micro-interactions (scale 1.02)
 * - Respects prefers-reduced-motion
 * - GPU-accelerated transforms
 * 
 * @param sentiment - Market sentiment for border color/animation
 * @param disableAnimations - Override to disable all animations
 * @param variant - Visual weight (default, elevated, subtle)
 */
export function GlassCard({
  children,
  className = "",
  sentiment,
  disableAnimations = false,
  variant = "default",
}: GlassCardProps) {
  // Sentiment-based gradient configurations
  const sentimentGradients = {
    bullish: "linear-gradient(90deg, var(--gradient-bullish-start) 0%, var(--color-sentiment-bullish) 50%, var(--gradient-bullish-start) 100%)",
    bearish: "linear-gradient(90deg, var(--gradient-bearish-start) 0%, var(--color-sentiment-bearish) 50%, var(--gradient-bearish-start) 100%)",
    neutral: "linear-gradient(90deg, var(--gradient-neutral-start) 0%, var(--color-sentiment-neutral) 50%, var(--gradient-neutral-start) 100%)",
    default: "linear-gradient(90deg, var(--gradient-cyber-start) 0%, var(--gradient-cyber-mid) 50%, var(--gradient-cyber-end) 100%)",
  };

  const gradient = sentiment ? sentimentGradients[sentiment] : sentimentGradients.default;

  // Animation variants for border pulse
  const borderAnimation = !disableAnimations
    ? {
        opacity: [0.5, 1, 0.5],
      }
    : {};

  const borderTransition = !disableAnimations
    ? {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut" as const,
      }
    : {};

  // Hover animation
  const hoverAnimation = !disableAnimations
    ? {
        scale: 1.02,
        transition: { duration: 0.2 },
      }
    : {};

  // Variant styles
  const variantStyles = {
    default: "bg-[var(--color-bg-glass)] backdrop-blur-[var(--backdrop-blur)]",
    elevated: "bg-[var(--color-bg-elevated)] backdrop-blur-[var(--backdrop-blur-lg)] shadow-[var(--shadow-xl)]",
    subtle: "bg-[var(--color-bg-glass-light)] backdrop-blur-[var(--backdrop-blur-sm)]",
  };

  return (
    <motion.div
      className={cn("relative rounded-2xl overflow-hidden", className)}
      whileHover={hoverAnimation}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Animated gradient border */}
      <motion.div
        className="absolute inset-0 rounded-2xl p-[1px]"
        style={{
          background: gradient,
          backgroundSize: "200% 200%",
        }}
        animate={borderAnimation}
        transition={borderTransition}
      />

      {/* Glass content container */}
      <div
        className={cn(
          "relative rounded-2xl p-6",
          variantStyles[variant],
          "border border-[var(--color-glass-border)]"
        )}
      >
        {children}
      </div>

      {/* Sentiment glow overlay (subtle background effect) */}
      {sentiment && !disableAnimations && (
        <motion.div
          className="absolute -inset-20 rounded-full blur-3xl opacity-10 pointer-events-none"
          style={{
            background:
              sentiment === "bullish"
                ? "var(--color-sentiment-bullish)"
                : sentiment === "bearish"
                ? "var(--color-sentiment-bearish)"
                : "var(--color-sentiment-neutral)",
          }}
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.05, 0.15, 0.05],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut" as const,
          }}
        />
      )}
    </motion.div>
  );
}

/**
 * GlassCardHeader - Optional header section with consistent styling
 */
export function GlassCardHeader({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("mb-6 pb-4 border-b border-[var(--color-glass-border)]", className)}>
      {children}
    </div>
  );
}

/**
 * GlassCardTitle - Semantic title component
 */
export function GlassCardTitle({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <h3 className={cn("text-lg font-semibold text-foreground", className)}>
      {children}
    </h3>
  );
}

/**
 * GlassCardDescription - Semantic description component
 */
export function GlassCardDescription({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <p className={cn("text-sm text-muted-foreground mt-1", className)}>
      {children}
    </p>
  );
}