import { SignIn } from "@clerk/nextjs";
import { Suspense } from "react";

function LoadingState() {
    return (
        <div className="flex flex-col items-center justify-center p-8">
            <div className="w-8 h-8 border-2 border-neon-green border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-4 text-gray-400 text-sm animate-pulse">Establishing Secure Connection...</p>
        </div>
    );
}

export default function Page() {
    return (
        <div className="flex items-center justify-center min-h-screen bg-black/90 backdrop-blur-xl">
            <div className="p-8 border border-white/10 rounded-2xl bg-black/50 shadow-2xl shadow-neon-green/20 relative overflow-hidden">
                {/* Background Decoration */}
                <div className="absolute -top-10 -right-10 w-40 h-40 bg-neon-green/10 rounded-full blur-3xl pointer-events-none"></div>

                <h1 className="text-3xl font-bold text-center mb-8 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 relative z-10">
                    Axiom Access
                </h1>

                <div className="relative z-10 min-w-[320px]">
                    <Suspense fallback={<LoadingState />}>
                        <SignIn
                            afterSignInUrl="/dashboard"
                            redirectUrl="/dashboard"
                            appearance={{
                                elements: {
                                    formButtonPrimary: 'bg-neon-green hover:bg-neon-green/80 text-black font-bold transition-all duration-300',
                                    card: 'bg-transparent shadow-none w-full',
                                    headerTitle: 'hidden',
                                    headerSubtitle: 'text-gray-400',
                                    socialButtonsBlockButton: 'border-white/20 hover:bg-white/5 text-white transition-all duration-200',
                                    formFieldLabel: 'text-gray-400',
                                    formFieldInput: 'bg-white/5 border-white/10 text-white focus:border-neon-green transition-colors',
                                    footerActionLink: 'text-neon-green hover:text-neon-green/80 transition-colors',
                                    identityPreviewText: 'text-gray-300',
                                    formFieldInputShowPasswordButton: 'text-gray-400 hover:text-white',
                                    alertText: 'text-red-400' // Better error visibility
                                },
                                layout: {
                                    socialButtonsPlacement: 'bottom',
                                    showOptionalFields: false
                                }
                            }}
                        />
                    </Suspense>
                </div>
            </div>
        </div>
    );
}
