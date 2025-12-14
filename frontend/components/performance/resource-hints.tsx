"use client";

import React from 'react';

interface ResourceHintsProps {
  apiUrl?: string;
}

export default function ResourceHints({ apiUrl }: ResourceHintsProps) {
  React.useEffect(() => {
    if (!apiUrl) return;

    // DNS prefetch for external API
    const dnsPrefetch = document.createElement('link');
    dnsPrefetch.rel = 'dns-prefetch';
    dnsPrefetch.href = apiUrl;
    document.head.appendChild(dnsPrefetch);

    // Preconnect to external API
    const preconnect = document.createElement('link');
    preconnect.rel = 'preconnect';
    preconnect.href = apiUrl;
    preconnect.crossOrigin = 'anonymous';
    document.head.appendChild(preconnect);

    // Preload critical fonts (check if they exist first)
    const fontPaths = [
      '/_next/static/media/797e433ab948586e-s.p.dbea232f.woff2',
      '/_next/static/media/caa3a2e1cccd8315-s.p.853070df.woff2'
    ];

    fontPaths.forEach(fontPath => {
      const fontLink = document.createElement('link');
      fontLink.rel = 'preload';
      fontLink.href = fontPath;
      fontLink.as = 'font';
      fontLink.type = 'font/woff2';
      fontLink.crossOrigin = 'anonymous';
      document.head.appendChild(fontLink);
    });

    // Cleanup function
    return () => {
      document.head.removeChild(dnsPrefetch);
      document.head.removeChild(preconnect);
      fontPaths.forEach(fontPath => {
        const existingLink = document.querySelector(`link[href="${fontPath}"]`) as HTMLLinkElement;
        if (existingLink && document.head.contains(existingLink)) {
          document.head.removeChild(existingLink);
        }
      });
    };
  }, [apiUrl]);

  return null; // This component only adds resource hints via useEffect
}