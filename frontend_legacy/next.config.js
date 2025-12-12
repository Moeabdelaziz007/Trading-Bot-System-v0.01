const createNextIntlPlugin = require('next-intl/plugin');
const withBundleAnalyzer = require('@next/bundle-analyzer')({
    enabled: process.env.ANALYZE === 'true',
});

const withNextIntl = createNextIntlPlugin();

/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    
    // ━━━ 🚀 Build Optimization | تحسين البناء ━━━
    swcMinify: true,
    compiler: {
        removeConsole: process.env.NODE_ENV === 'production',
    },
    
    // ━━━ 📁 TypeScript Configuration ━━━
    typescript: {
        // Ignore build errors during deployment
        ignoreBuildErrors: false,
    },
    
    // ━━━ 📂 Page Extensions & Exclusions ━━━
    pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
    // Exclude legacy directory from build (symlink to legacy-components)
    webpack: (config, { isServer }) => {
        config.watchOptions = {
            ...config.watchOptions,
            ignored: ['**/src/legacy/**', '**/legacy-components/**'],
        };
        return config;
    },
    
    // ━━━ 🔐 Security Headers | رؤوس الأمان ━━━
    async headers() {
        return [
            {
                source: '/:path*',
                headers: [
                    { key: 'X-DNS-Prefetch-Control', value: 'on' },
                    { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
                    { key: 'X-Content-Type-Options', value: 'nosniff' },
                    { key: 'X-Frame-Options', value: 'DENY' },
                    { key: 'X-XSS-Protection', value: '1; mode=block' },
                    { key: 'Referrer-Policy', value: 'origin-when-cross-origin' },
                    { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
                ],
            },
        ];
    },
    
    // ━━━ 🔄 API Rewrites | إعادة توجيه API ━━━
    async rewrites() {
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://trading-brain-v1.amrikyy.workers.dev';
        return [
            {
                source: '/api/backend/:path*',
                destination: `${backendUrl}/:path*`,
            },
        ];
    },
    
    // ━━━ 🖼 Image Optimization | تحسين الصور ━━━
    images: {
        domains: ['avatars.githubusercontent.com', 'lh3.googleusercontent.com'],
        formats: ['image/avif', 'image/webp'],
    },
    
    // ━━━ 📦 Output Configuration ━━━
    output: 'standalone',
};

module.exports = withBundleAnalyzer(withNextIntl(nextConfig));
