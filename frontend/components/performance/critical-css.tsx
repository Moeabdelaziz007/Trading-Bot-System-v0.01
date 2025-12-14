'use client';

import { useEffect } from 'react';

// Critical CSS for above-the-fold content to prevent FOUC
const criticalCSS = `
  /* Critical above-the-fold styles */
  body {
    background: #000;
    color: #e5e7eb;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  margin: 0;
    padding: 0;
  -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  
  /* Preload critical layout styles */
  .min-h-screen {
    min-height: 100vh;
  }
  
  .bg-black {
    background-color: #000;
  }
  
  .text-gray-200 {
    color: #e5e7eb;
  }
  
  .font-mono {
    font-family: ui-monospace, SFMono-Regular, 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace;
  }
  
  /* Prevent layout shift */
  .relative {
    position: relative;
  }
  
  .z-10 {
    z-index: 10;
  }
  
  .max-w-7xl {
    max-width: 80rem;
  }
  
  .mx-auto {
    margin-left: auto;
    margin-right: auto;
  }
  
  /* Optimize text rendering */
  .text-lg {
    font-size: 1.125rem;
    line-height: 1.75rem;
  }
  
  .font-bold {
    font-weight: 700;
  }
  
  .text-white {
    color: #ffffff;
  }
  
  /* Prevent flash of unstyled content */
  .transition-all {
    transition: all 0.3s ease;
  }
  
  .border-cyan-500\\/20 {
    border-color: rgba(6, 182, 212, 0.2);
  }
  
  .pb-6 {
    padding-bottom: 1.5rem;
  }
`;

interface CriticalCSSProps {
  children: React.ReactNode;
}

export default function CriticalCSS({ children }: CriticalCSSProps) {
  useEffect(() => {
    // Inject critical CSS immediately to prevent FOUC
    const style = document.createElement('style');
    style.textContent = criticalCSS;
    style.id = 'critical-css';
    document.head.appendChild(style);

    // Remove after page load to prevent conflicts
    const removeStyle = () => {
      if (document.getElementById('critical-css')) {
        document.head.removeChild(style);
      }
    };

    // Remove after initial paint
    if (window.requestIdleCallback) {
      window.requestIdleCallback(removeStyle);
    } else {
      setTimeout(removeStyle, 100);
    }
  }, []);

  return <>{children}</>;
}