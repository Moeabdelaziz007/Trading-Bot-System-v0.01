import { SignUp } from "@clerk/nextjs";
import { dark } from "@clerk/themes";
import { Suspense } from "react";

function LoadingState() {
    return (
        <div className="flex flex-col items-center justify-center p-8">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-4 text-gray-400 text-sm animate-pulse">Initializing Registration...</p>
        </div>
    );
}

export default function SignUpPage() {
    return (
        <div className="flex min-h-screen w-full bg-[#050505] text-white overflow-hidden font-sans items-center justify-center">
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:24px_24px]"></div>

            <div className="z-10 w-full max-w-md px-6">
                <Suspense fallback={<LoadingState />}>
                    <SignUp
                        afterSignUpUrl="/dashboard"
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
                                headerTitle: "text-2xl font-bold text-white mb-1",
                                headerSubtitle: "text-gray-500 text-sm mb-6",
                                formButtonPrimary: "bg-blue-600 hover:bg-blue-500 text-white transition-all duration-300",
                                formFieldInput: "bg-[#111] border-white/5 focus:border-blue-500/50 h-11",
                                formFieldLabel: "text-gray-400 text-xs uppercase tracking-wider mb-1.5",
                                footerActionLink: "text-blue-400 hover:text-blue-300 font-medium",
                                socialButtonsBlockButton: "bg-white/5 border border-white/5 hover:bg-white/10 h-11",
                                socialButtonsBlockButtonText: "text-gray-300 font-medium",
                            }
                        }}
                    />
                </Suspense>
            </div>
        </div>
    );
}
