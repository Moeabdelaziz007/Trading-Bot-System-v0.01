import type React from "react"
import type { Metadata, Viewport } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"

const _geist = Geist({ subsets: ["latin"], variable: '--font-geist' })
const _geistMono = Geist_Mono({ subsets: ["latin"], variable: '--font-geist-mono' })

// Theme color for browser bar (Elite Level)
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0a0a0a",
}

export const metadata: Metadata = {
  title: "AlphaQuanTopology (AQT)",
  description: "AI-Powered Quantum Trading Dashboard - Real-time neural signal analysis",
  generator: "v0.app",

  // PWA Manifest
  manifest: "/manifest.json",

  // Elite Icons Strategy (Dynamic Dark/Light + Safari Pinned Tab)
  icons: {
    icon: [
      { url: "/icon-light-32x32.png", media: "(prefers-color-scheme: light)" },
      { url: "/icon-dark-32x32.png", media: "(prefers-color-scheme: dark)" },
      { url: "/favicon.ico" }, // Fallback
    ],
    shortcut: ["/favicon.ico"],
    apple: [
      { url: "/apple-icon.png", sizes: "180x180", type: "image/png" },
    ],
    other: [
      {
        rel: "mask-icon", // Safari Pinned Tab
        url: "/safari-pinned-tab.svg",
        color: "#39FF14", // Neon green brand color
      },
    ],
  },

  // Open Graph (Facebook, LinkedIn, etc.)
  openGraph: {
    title: "AlphaQuanTopology | AI Trading",
    description: "Real-time AI logic and execution dashboard.",
    url: "https://aqt.axiomid.app",
    siteName: "AxiomID Platform",
    images: [
      {
        url: "https://aqt.axiomid.app/api/og",
        width: 1200,
        height: 630,
        alt: "AQT Dashboard Interface",
      },
    ],
    locale: "en_US",
    type: "website",
  },

  // Twitter / X Cards
  twitter: {
    card: "summary_large_image",
    title: "AlphaQuanTopology (AQT)",
    description: "Execute trades with Quantum AI precision.",
    images: ["https://aqt.axiomid.app/twitter-image.png"],
  },
}

import { AuthProvider } from "@/contexts/AuthContext"

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <head>
      </head>
      <body className={`font-sans antialiased ${_geist.variable} ${_geistMono.variable}`}>
        <AuthProvider>
          {children}
        </AuthProvider>
        <Analytics />
      </body>
    </html>
  )
}

