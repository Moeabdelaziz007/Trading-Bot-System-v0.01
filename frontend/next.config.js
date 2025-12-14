/** @type {import('next').NextConfig} */
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

const nextConfig = withBundleAnalyzer({
  // Add empty turbopack config to avoid the error
  turbopack: {},
  
  // Optimize chunks
  experimental: {
    optimizePackageImports: [
      'framer-motion',
      'lucide-react',
      'date-fns'
    ]
  },
  
  // Optimize images
  images: {
    formats: ['image/webp', 'image/avif'],
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days
  },
  
  // Compress output
  compress: true,
  
  // Enable static optimization
  poweredByHeader: false,
  
  // Disable source maps in production for better performance
  productionBrowserSourceMaps: false,
  
  // Configure headers for better caching
  async headers() {
    return [
      {
        source: '/_next/static/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          }
        ]
      },
      {
        source: '/api/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-store, max-age=0'
          }
        ]
      }
    ];
  }
});

module.exports = nextConfig;