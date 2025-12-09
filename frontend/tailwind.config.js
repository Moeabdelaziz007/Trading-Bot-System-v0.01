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
      },
      colors: {
        axiom: {
          bg: '#0D0D0D',
          card: '#1A1A2E',
          surface: '#16213E',
          primary: '#00FF88', // Toxic Green
          secondary: '#00D9FF', // Electric Cyan
          tertiary: '#FF00FF', // Magenta
          warning: '#FFD700', // Gold
          danger: '#FF4444', // Neon Red
          purple: '#8B5CF6',
          orange: '#FF6B35'
        }
      },
      backgroundImage: {
        'carbon-fiber': 'radial-gradient(circle at center, #222 1px, transparent 1px)',
      }
    },
  },
  plugins: [],
}