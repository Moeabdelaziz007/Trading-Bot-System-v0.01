/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        arabic: ['Cairo', 'Tajawal', 'sans-serif'],
      },
      colors: {
        // AlphaAxiom v1.0 Citadel Edition Color System
        axiom: {
          // Backgrounds
          bg: '#050505',
          surface: '#0A0A1A',

          // Neon Accents
          'neon-cyan': '#00FFFF',      // AI/Intelligence/Core
          'neon-purple': '#A855F7',    // Strategy/Learning
          'neon-green': '#22C55E',     // Profit/Buy/Success
          'neon-red': '#EF4444',       // Loss/Sell/Danger
          'neon-gold': '#FFD700',      // Premium/VIP/Grandmaster
          'neon-magenta': '#FF0055',   // Shadow Agent
          'neon-blue': '#3B82F6',      // Info/Capital.com
          'neon-orange': '#FF6B35',    // Workers AI

          // Legacy colors (keep for compatibility)
          card: '#1A1A2E',
          primary: '#00FF88',
          secondary: '#00D9FF',
          tertiary: '#FF00FF',
          warning: '#FFD700',
          danger: '#FF4444',
          purple: '#8B5CF6',
          orange: '#FF6B35'
        },
        // Text colors
        text: {
          primary: '#FFFFFF',
          muted: '#9CA3AF',
          dim: '#6B7280',
        },
        // Glass effects
        glass: {
          border: 'rgba(255,255,255,0.1)',
        }
      },
      backgroundImage: {
        'carbon-fiber': 'linear-gradient(45deg, #1a1a1a 25%, transparent 25%, transparent 75%, #1a1a1a 75%, #1a1a1a), linear-gradient(45deg, #1a1a1a 25%, transparent 25%, transparent 75%, #1a1a1a 75%, #1a1a1a)',
      },
      boxShadow: {
        'glow-cyan': '0 0 20px rgba(0,255,255,0.3)',
        'glow-purple': '0 0 20px rgba(168,85,247,0.3)',
        'glow-gold': '0 0 20px rgba(255,215,0,0.3)',
        'glow-green': '0 0 20px rgba(34,197,94,0.3)',
        'glow-red': '0 0 20px rgba(239,68,68,0.3)',
      },
      backdropBlur: {
        'glass': '12px',
      }
    },
  },
  plugins: [],
}