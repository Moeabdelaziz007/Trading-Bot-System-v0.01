"use client";

import React, { useState, useEffect } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Simulate cinematic loading time
        const timer = setTimeout(() => {
            setIsLoading(false);
        }, 2000);

        // Cleanup to prevent memory leaks
        return () => clearTimeout(timer);
    }, []);

    if (isLoading) {
        return (
            <div className="fixed inset-0 bg-black flex items-center justify-center z-50">
                <div className="flex flex-col items-center">
                    <div className="w-16 h-16 border-4 border-axiom-primary border-t-transparent rounded-full animate-spin shadow-[0_0_20px_rgba(0,255,136,0.5)]"></div>
                    <h2 className="mt-4 text-xl font-bold text-white tracking-widest animate-pulse">AXIOM ANTIGRAVITY</h2>
                    <p className="text-axiom-secondary text-sm mt-2">Initializing Systems...</p>
                </div>
            </div>
        );
    }

    return <>{children}</>;
}
