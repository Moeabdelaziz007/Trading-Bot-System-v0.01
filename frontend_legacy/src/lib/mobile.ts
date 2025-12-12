/**
 * 📱 Mobile Responsive Utilities for Axiom Antigravity
 * Custom hooks and utilities for mobile-first design
 * 
 * Features:
 * - Viewport detection
 * - Touch device detection
 * - Safe area handling
 * - Orientation detection
 */

import { useState, useEffect } from 'react';

// Breakpoints matching Tailwind defaults
export const BREAKPOINTS = {
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
    '2xl': 1536,
} as const;

type Breakpoint = keyof typeof BREAKPOINTS;

/**
 * Hook to detect current viewport size
 */
export function useViewport() {
    const [viewport, setViewport] = useState({
        width: typeof window !== 'undefined' ? window.innerWidth : 1024,
        height: typeof window !== 'undefined' ? window.innerHeight : 768,
    });

    useEffect(() => {
        const handleResize = () => {
            setViewport({
                width: window.innerWidth,
                height: window.innerHeight,
            });
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    return viewport;
}

/**
 * Hook to check if viewport matches a breakpoint
 */
export function useBreakpoint(breakpoint: Breakpoint) {
    const { width } = useViewport();
    return width >= BREAKPOINTS[breakpoint];
}

/**
 * Hook to detect if device is mobile
 */
export function useIsMobile() {
    const { width } = useViewport();
    return width < BREAKPOINTS.md;
}

/**
 * Hook to detect if device is tablet
 */
export function useIsTablet() {
    const { width } = useViewport();
    return width >= BREAKPOINTS.md && width < BREAKPOINTS.lg;
}

/**
 * Hook to detect if device is desktop
 */
export function useIsDesktop() {
    const { width } = useViewport();
    return width >= BREAKPOINTS.lg;
}

/**
 * Hook to detect touch device
 */
export function useIsTouchDevice() {
    const [isTouch, setIsTouch] = useState(false);

    useEffect(() => {
        const checkTouch = () => {
            setIsTouch(
                'ontouchstart' in window ||
                navigator.maxTouchPoints > 0
            );
        };
        checkTouch();
    }, []);

    return isTouch;
}

/**
 * Hook to detect device orientation
 */
export function useOrientation() {
    const [orientation, setOrientation] = useState<'portrait' | 'landscape'>('portrait');

    useEffect(() => {
        const handleOrientationChange = () => {
            setOrientation(
                window.innerHeight > window.innerWidth ? 'portrait' : 'landscape'
            );
        };

        handleOrientationChange();
        window.addEventListener('resize', handleOrientationChange);
        return () => window.removeEventListener('resize', handleOrientationChange);
    }, []);

    return orientation;
}

/**
 * Hook for reduced motion preference
 */
export function useReducedMotion() {
    const [reducedMotion, setReducedMotion] = useState(false);

    useEffect(() => {
        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        setReducedMotion(mediaQuery.matches);

        const handleChange = (e: MediaQueryListEvent) => {
            setReducedMotion(e.matches);
        };

        mediaQuery.addEventListener('change', handleChange);
        return () => mediaQuery.removeEventListener('change', handleChange);
    }, []);

    return reducedMotion;
}

/**
 * CSS class helpers for mobile
 */
export const mobileClasses = {
    // Touch-friendly button
    touchButton: 'min-h-touch min-w-touch p-3 active:scale-95 transition-transform touch-manipulation',

    // Full-width on mobile
    mobileFullWidth: 'w-full md:w-auto',

    // Stack on mobile, row on desktop
    mobileStack: 'flex flex-col md:flex-row gap-4',

    // Hide on mobile
    hideOnMobile: 'hidden md:block',

    // Show only on mobile
    showOnMobile: 'block md:hidden',

    // Safe area padding
    safeAreaPadding: 'pb-safe-bottom pt-safe-top',

    // Mobile card
    mobileCard: 'p-4 md:p-6 rounded-mobile',

    // Mobile text sizes
    mobileText: 'text-mobile-sm md:text-base',
    mobileHeading: 'text-lg md:text-xl font-bold',
};

/**
 * Get responsive value based on breakpoint
 */
export function getResponsiveValue<T>(
    mobile: T,
    tablet?: T,
    desktop?: T
): T {
    if (typeof window === 'undefined') return mobile;

    const width = window.innerWidth;

    if (width >= BREAKPOINTS.lg && desktop !== undefined) return desktop;
    if (width >= BREAKPOINTS.md && tablet !== undefined) return tablet;
    return mobile;
}
