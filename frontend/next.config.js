const createNextIntlPlugin = require('next-intl/plugin');

const withNextIntl = createNextIntlPlugin();

/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: 'https://trading-brain-v1.amrikyy.workers.dev/api/:path*',
            },
        ];
    },
};

module.exports = withNextIntl(nextConfig);
