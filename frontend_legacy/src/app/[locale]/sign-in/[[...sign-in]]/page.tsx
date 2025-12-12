import { SignIn } from "@clerk/nextjs";
import { dark } from "@clerk/themes";
import { Suspense } from "react";

// Loading state with Suspense (from Jules)
function LoadingState() {
    return (
        <div className="flex flex-col items-center justify-center p-8">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-4 text-gray-400 text-sm animate-pulse">Establishing Secure Connection...</p>
        </div>
    );
}

export default function CustomSignInPage() {
    return (
        <div className="flex min-h-screen w-full bg-[#050505] text-white overflow-hidden font-sans">

            {/* 🔮 Left Section: Cinematic/Artistic Side */}
            <div className="hidden lg:flex w-1/2 flex-col justify-center items-center relative p-12 overflow-hidden">
                {/* Dynamic Background Effects */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#0a0f1e] via-[#050505] to-[#0a0a0a] z-0" />
                <div className="absolute top-0 left-0 w-full h-full opacity-20 z-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />

                {/* Glowing Orbs/Accents */}
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-[120px] animate-pulse-slow"></div>
                <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-600/10 rounded-full blur-[100px] animate-pulse-slower"></div>

                <div className="z-10 text-center space-y-8 relative">
                    <div className="relative inline-block group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-cyan-500 rounded-lg blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
                        <h1 className="relative text-7xl font-bold tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-100 to-gray-400 font-orbitron">
                            ALPHA AXIOM
                        </h1>
                    </div>

                    <p className="text-xl text-gray-400 font-light max-w-md mx-auto leading-relaxed border-l-2 border-blue-500/30 pl-6 text-left">
                        Advanced Intelligence <br />for Modern Trading.
                    </p>

                    <div className="flex items-center justify-center gap-4 pt-4">
                        <Badge text="SYSTEM v2.4" color="bg-blue-500/10 text-blue-400 border-blue-500/20" />
                        <Badge text="NEURAL BRIDGE ACTIVE" color="bg-green-500/10 text-green-400 border-green-500/20" />
                    </div>
                </div>

                {/* Futuristic Status Element */}
                <div className="absolute bottom-12 left-12 right-12 flex justify-between items-end border-t border-white/5 pt-6">
                    <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-ping"></div>
                        <span className="text-xs font-mono text-gray-500 tracking-widest">OPERATIONAL STATUS: NOMINAL</span>
                    </div>
                    <div className="text-right">
                        <span className="text-[10px] text-gray-600 font-mono block">SESSION ID</span>
                        <span className="text-xs text-gray-400 font-mono">AX-9920-XF</span>
                    </div>
                </div>
            </div>

            {/* 🔐 Right Section: Login Form */}
            <div className="w-full lg:w-1/2 flex items-center justify-center relative bg-[#050505]">
                {/* Subtle Grid Background */}
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:24px_24px]"></div>

                <div className="z-10 w-full max-w-md px-6">
                    <Suspense fallback={<LoadingState />}>
                        <SignIn
                            afterSignInUrl="/dashboard"
                            redirectUrl="/dashboard"
                            appearance={{
                                baseTheme: dark,
                                layout: {
                                    socialButtonsPlacement: "bottom",
                                    socialButtonsVariant: "blockButton",
                                    showOptionalFields: false,
                                },
                                variables: {
                                    colorPrimary: "#2563EB",
                                    colorBackground: "#0A0A0A",
                                    colorText: "white",
                                    colorTextSecondary: "#9CA3AF",
                                    colorInputBackground: "#111",
                                    colorInputText: "white",
                                    borderRadius: "0.75rem",
                                },
                                elements: {
                                    rootBox: "w-full",
                                    card: "bg-[#0A0A0A]/80 backdrop-blur-xl border border-white/10 shadow-[0_0_40px_-10px_rgba(37,99,235,0.1)] rounded-2xl p-8",
                                    headerTitle: "text-2xl font-bold text-white mb-1 font-orbitron tracking-wide",
                                    headerSubtitle: "text-gray-500 text-sm mb-6",
                                    formButtonPrimary: "bg-blue-600 hover:bg-blue-500 text-white transition-all duration-300 shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:shadow-[0_0_30px_rgba(37,99,235,0.5)] border-none h-11",
                                    formFieldInput: "bg-[#111] border-white/5 focus:border-blue-500/50 hover:border-white/10 transition-colors h-11 text-[15px]",
                                    formFieldLabel: "text-gray-400 text-xs uppercase tracking-wider mb-1.5",
                                    footerActionLink: "text-blue-400 hover:text-blue-300 font-medium",
                                    identityPreviewText: "text-gray-300",
                                    identityPreviewEditButton: "text-blue-400",
                                    dividerLine: "bg-white/10",
                                    dividerText: "text-gray-600 uppercase text-[10px] tracking-widest",
                                    socialButtonsBlockButton: "bg-white/5 border border-white/5 hover:bg-white/10 transition-colors h-11",
                                    socialButtonsBlockButtonText: "text-gray-300 font-medium",
                                    alert: "bg-red-500/10 border border-red-500/20 text-red-400",
                                    alertText: "text-red-400",
                                    formFieldAction: "text-blue-400 hover:text-blue-300",
                                    formFieldInputShowPasswordButton: "text-gray-400 hover:text-white",
                                }
                            }}
                        />
                    </Suspense>

                    <div className="mt-8 text-center">
                        <p className="text-[10px] text-gray-600 hover:text-gray-500 transition-colors cursor-pointer">
                            SECURED BY <span className="font-bold text-gray-500">CLERK</span> & <span className="font-bold text-gray-500">CLOUDFLARE</span>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

const Badge = ({ text, color }: { text: string, color: string }) => (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider border ${color}`}>
        {text}
    </span>
);
