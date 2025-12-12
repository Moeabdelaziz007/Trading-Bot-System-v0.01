/**
 * 🎭 Shared Animation Variants for Axiom Antigravity
 * Reusable Framer Motion animation configurations
 * 
 * Best Practices Applied:
 * - GPU-accelerated transforms (scale, opacity, y)
 * - 200-300ms transitions for UI responsiveness
 * - Spring physics for natural feel
 * - Stagger for sequential entrance
 */

// ==========================================
// 📦 CONTAINER VARIANTS (Parent elements)
// ==========================================

export const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1,
            delayChildren: 0.05
        }
    },
    exit: {
        opacity: 0,
        transition: {
            staggerChildren: 0.05,
            staggerDirection: -1
        }
    }
};

export const staggerContainerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.15,
            delayChildren: 0.1
        }
    }
};

// ==========================================
// 🎯 ITEM VARIANTS (Child elements)
// ==========================================

export const fadeInUp = {
    hidden: { opacity: 0, y: 20 },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            type: "spring",
            stiffness: 300,
            damping: 24
        }
    }
};

export const fadeInScale = {
    hidden: { opacity: 0, scale: 0.9 },
    visible: {
        opacity: 1,
        scale: 1,
        transition: {
            type: "spring",
            stiffness: 400,
            damping: 25
        }
    }
};

export const slideInLeft = {
    hidden: { opacity: 0, x: -30 },
    visible: {
        opacity: 1,
        x: 0,
        transition: {
            type: "spring",
            stiffness: 300,
            damping: 24
        }
    }
};

export const slideInRight = {
    hidden: { opacity: 0, x: 30 },
    visible: {
        opacity: 1,
        x: 0,
        transition: {
            type: "spring",
            stiffness: 300,
            damping: 24
        }
    }
};

// ==========================================
// ✨ INTERACTION VARIANTS (Hover, Tap)
// ==========================================

export const hoverScale = {
    scale: 1.02,
    transition: { duration: 0.2 }
};

export const hoverScaleLarge = {
    scale: 1.05,
    transition: { duration: 0.2 }
};

export const tapScale = {
    scale: 0.98
};

export const hoverGlow = {
    boxShadow: "0 0 20px rgba(0, 240, 255, 0.3)",
    transition: { duration: 0.3 }
};

// ==========================================
// 📊 CHART & DATA VARIANTS
// ==========================================

export const progressBarVariants = {
    hidden: { width: 0 },
    visible: (percentage: number) => ({
        width: `${percentage}%`,
        transition: {
            duration: 1,
            delay: 0.3,
            ease: [0.4, 0, 0.2, 1]
        }
    })
};

export const numberCountUp = {
    hidden: { opacity: 0, scale: 0.5 },
    visible: {
        opacity: 1,
        scale: 1,
        transition: {
            type: "spring",
            delay: 0.2
        }
    }
};

// ==========================================
// 📱 PAGE TRANSITION VARIANTS
// ==========================================

export const pageTransition = {
    initial: { opacity: 0, y: 10 },
    animate: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.3,
            ease: [0.4, 0, 0.2, 1]
        }
    },
    exit: {
        opacity: 0,
        y: -10,
        transition: {
            duration: 0.2
        }
    }
};

// ==========================================
// 🔄 LOADING VARIANTS
// ==========================================

export const pulseVariants = {
    animate: {
        scale: [1, 1.05, 1],
        opacity: [0.7, 1, 0.7],
        transition: {
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut"
        }
    }
};

export const skeletonVariants = {
    animate: {
        background: [
            "linear-gradient(90deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.02) 100%)",
            "linear-gradient(90deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 50%, rgba(255,255,255,0.05) 100%)"
        ],
        transition: {
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut"
        }
    }
};

// ==========================================
// 🌟 SPECIAL EFFECTS
// ==========================================

export const glowPulse = {
    animate: {
        boxShadow: [
            "0 0 0px rgba(0, 240, 255, 0)",
            "0 0 15px rgba(0, 240, 255, 0.5)",
            "0 0 0px rgba(0, 240, 255, 0)"
        ],
        transition: {
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
        }
    }
};

export const floatAnimation = {
    animate: {
        y: [0, -5, 0],
        transition: {
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut"
        }
    }
};
