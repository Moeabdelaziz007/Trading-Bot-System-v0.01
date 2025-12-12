"use client";

import { useEffect, useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // First 5 Seconds Rule: 2.5s Preloader
        const timer = setTimeout(() => {
            setIsLoading(false);
        }, 2200);

        return () => clearTimeout(timer);
    }, []);

    return (
        <>
            {/* Cinematic Preloader */}
            <div
                className={`fixed inset-0 bg-black z-[9999] flex items-center justify-center transition-opacity duration-700 ease-in-out ${isLoading ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
            >
                <div className="relative flex flex-col items-center">
                    {/* Pulsing Logo/Text */}
                    <div className="relative">
                        <div className="absolute -inset-4 bg-blue-500/20 rounded-full blur-xl animate-pulse"></div>
                        <h1 className="relative text-3xl md:text-5xl font-bold tracking-[0.2em] text-white font-orbitron animate-pulse">
                            ALPHA AXIOM
                        </h1>
                    </div>

                    {/* Futuristic Loader Bar */}
                    <div className="mt-8 w-48 h-1 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-blue-600 to-cyan-400 w-full animate-[loading_2s_ease-in-out_infinite] origin-left"></div>
                    </div>

                    <p className="mt-4 text-[10px] text-gray-500 tracking-widest font-mono">INITIALIZING SYSTEM v2.4</p>
                </div>
            </div>

            {/* Main Content (Fade In) */}
            <div className={`transition-opacity duration-1000 delay-300 ${isLoading ? 'opacity-0' : 'opacity-100'}`}>
                {children}
            </div>

            {/* Animated Loading Bar Keyframes */}
            <style dangerouslySetInnerHTML={{
                __html: `
                @keyframes loading {
                    0% { transform: translateX(-100%); }
                    50% { transform: translateX(0%); }
                    100% { transform: translateX(100%); }
                }
            ` }} />
        </>
    );
}
