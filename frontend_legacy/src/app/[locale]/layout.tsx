import type { Metadata, Viewport } from "next";
import { JetBrains_Mono, Cairo, Orbitron, Inter } from "next/font/google";
import { NextIntlClientProvider } from 'next-intl';
import { getMessages, setRequestLocale } from 'next-intl/server';
import "../globals.css";
import { Providers } from "./providers";
import Link from "next/link";
import { ClerkProvider, SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";

const inter = Inter({ subsets: ["latin"], variable: '--font-inter' });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: '--font-jetbrains' });
const cairo = Cairo({ subsets: ["arabic"], variable: '--font-cairo', weight: ['400', '700'] });
const orbitron = Orbitron({ subsets: ["latin"], variable: '--font-orbitron', weight: ['400', '700', '900'] });

export const metadata: Metadata = {
    title: "Axiom Antigravity | AI Forex Trading",
    description: "AI-Powered Forex Trading Platform with GLM-4.5 Intelligence",
    manifest: "/manifest.json",
    openGraph: {
        title: "Axiom Antigravity Trading Hub",
        description: "AI-Powered Market Intelligence - Zero Latency, Zero Cost",
        images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "Axiom Antigravity" }],
        type: "website",
    },
    twitter: {
        card: "summary_large_image",
        title: "Axiom Antigravity Trading Hub",
        description: "AI-Powered Market Intelligence",
    },
    appleWebApp: {
        capable: true,
        statusBarStyle: "black-translucent",
        title: "Axiom Antigravity",
    },
    icons: {
        icon: "/icon.png",
        apple: "/icon.png",
    },
};

export const viewport: Viewport = {
    themeColor: "#00F0FF",
    width: "device-width",
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
};

// Generate static params for supported locales
export function generateStaticParams() {
    return [{ locale: 'en' }, { locale: 'ar' }];
}

export default async function RootLayout({
    children,
    params: { locale }
}: {
    children: React.ReactNode;
    params: { locale: string };
}) {
    // Enable static rendering for next-intl
    setRequestLocale(locale);

    const messages = await getMessages();
    const dir = locale === 'ar' ? 'rtl' : 'ltr';
    const fontVariable = locale === 'ar' ? cairo.variable : inter.variable;

    return (
        <html lang={locale} dir={dir} className="dark">
            <head>
                <link rel="apple-touch-icon" href="/icon.png" />
                <meta name="apple-mobile-web-app-capable" content="yes" />
                <meta name="mobile-web-app-capable" content="yes" />
            </head>
            <body className={`${inter.variable} ${cairo.variable} ${orbitron.variable} ${mono.variable} font-sans bg-[var(--void)] text-white min-h-screen`}>
                {/* Topographic Background */}
                <div className="topo-bg" />

                <ClerkProvider>
                    <NextIntlClientProvider messages={messages}>
                        <Providers>
                            {/* Premium Navigation Header */}
                            <header className="premium-nav fixed top-0 left-0 right-0 z-40 h-16 flex items-center justify-between px-6">
                                {/* Logo */}
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--neon-cyan)] to-[var(--neon-blue)] flex items-center justify-center">
                                        <span className="font-orbitron font-bold text-lg">A</span>
                                    </div>
                                    <div>
                                        <h1 className="text-sm font-bold font-orbitron tracking-wider">AXIOM</h1>
                                        <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest">Antigravity</p>
                                    </div>
                                </div>

                                {/* Nav Items */}
                                <nav className="hidden md:flex items-center gap-1">
                                    <Link href="/" className="nav-pill active">
                                        Dashboard
                                    </Link>
                                    <Link href="/bots" className="nav-pill">
                                        AI Bots
                                    </Link>
                                    <Link href="/test-ai" className="nav-pill">
                                        Test AI
                                    </Link>
                                    <Link href="/settings" className="nav-pill">
                                        Settings
                                    </Link>
                                    <Link href="/profile" className="nav-pill">
                                        Profile
                                    </Link>
                                    <Link href="/about" className="nav-pill">
                                        About
                                    </Link>
                                </nav>

                                {/* Right Side - Clerk Authentication */}
                                <div className="flex items-center gap-4">
                                    <SignedOut>
                                        <SignInButton />
                                    </SignedOut>
                                    <SignedIn>
                                        <UserButton
                                            appearance={{
                                                elements: {
                                                    avatarBox: "w-9 h-9 rounded-full border-2 border-[var(--neon-purple)]"
                                                }
                                            }}
                                        />
                                    </SignedIn>
                                </div>
                            </header>

                            {/* Main Content */}
                            <main className="pt-20 px-4 md:px-6 pb-8 max-w-7xl mx-auto">
                                {children}
                            </main>
                        </Providers>
                    </NextIntlClientProvider>
                </ClerkProvider>
            </body>
        </html>
    );
}