import type { Metadata, Viewport } from "next";
import { JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const mono = JetBrains_Mono({ subsets: ["latin"], variable: '--font-mono' });

export const metadata: Metadata = {
    title: "Antigravity Terminal",
    description: "AI-Powered Trading Terminal - Bloomberg Killer",
    manifest: "/manifest.json",
    appleWebApp: {
        capable: true,
        statusBarStyle: "black-translucent",
        title: "Antigravity",
    },
    icons: {
        icon: "/icon.png",
        apple: "/icon.png",
    },
};

export const viewport: Viewport = {
    themeColor: "#06b6d4",
    width: "device-width",
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" className="dark">
            <head>
                <link rel="apple-touch-icon" href="/icon.png" />
                <meta name="apple-mobile-web-app-capable" content="yes" />
                <meta name="mobile-web-app-capable" content="yes" />
            </head>
            <body className={`${mono.variable} font-mono bg-[#050505] text-white h-screen flex overflow-hidden selection:bg-cyan-500/30`}>

                {/* 🧭 Sidebar - Fixed on left */}
                <aside className="hidden md:flex flex-col w-64 flex-shrink-0 z-50">
                    <Sidebar />
                </aside>

                {/* 📊 Main Content - Scrollable */}
                <main className="flex-1 flex flex-col relative overflow-hidden bg-gradient-to-br from-[#050505] to-[#080808]">
                    {children}
                </main>

            </body>
        </html>
    );
}
