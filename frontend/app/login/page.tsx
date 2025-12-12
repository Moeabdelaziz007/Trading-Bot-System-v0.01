import { LoginForm } from "@/components/auth/login-form"

export default function LoginPage() {
    return (
        <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8 relative overflow-hidden">
            {/* Background decorations matching dashboard */}
            <div className="absolute inset-0 z-0 pointer-events-none opacity-20 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-zinc-900/0 via-zinc-900/0 to-zinc-950/80" />

            <div className="w-full max-w-md space-y-8 relative z-10">
                <div className="text-center">
                    <h2 className="mt-6 text-3xl font-bold tracking-tight text-white">
                        Axiom <span className="text-[#39FF14]">Access</span>
                    </h2>
                    <p className="mt-2 text-sm text-gray-400">
                        Sign in to access the Quantum Intelligence Layer
                    </p>
                </div>
                <LoginForm />
            </div>
        </div>
    )
}
