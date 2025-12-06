import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const mono = JetBrains_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "Antigravity Terminal",
    description: "AI-Powered Institutional Trading System",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={`${mono.className} bg-black text-white h-screen flex overflow-hidden`}>
                {/* Sidebar fixed on left */}
                <Sidebar />

                {/* Main content area */}
                <main className="flex-1 overflow-auto relative bg-[#030303]">
                    {children}
                </main>
            </body>
        </html>
    );
}
