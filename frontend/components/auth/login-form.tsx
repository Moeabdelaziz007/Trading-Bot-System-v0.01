"use client"

import { useState } from "react"
import { useAuth } from "@/contexts/AuthContext"
import { useRouter } from "next/navigation"
import { Github, Loader2, Mail, Phone, Lock } from "lucide-react"

export function LoginForm() {
    const { signInWithGoogle, signInWithEmail } = useAuth()
    const router = useRouter()
    const [loading, setLoading] = useState(false)
    const [mode, setMode] = useState<"email" | "phone">("email")

    // Form states
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [phoneNumber, setPhoneNumber] = useState("")

    const handleGoogleSignIn = async () => {
        try {
            setLoading(true)
            await signInWithGoogle()
            router.push("/") // Redirect to dashboard
        } catch (error) {
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    const handleEmailSignIn = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            setLoading(true)
            await signInWithEmail(email, password)
            router.push("/")
        } catch (error) {
            console.error(error)
            alert("Login failed")
        } finally {
            setLoading(false)
        }
    }

    const handlePhoneSignIn = (e: React.FormEvent) => {
        e.preventDefault()
        // Phone auth requires RecaptchaVerifier which is complex to set up in this snippet
        // keeping as placeholder/console log for now as requested plan was "correct login"
        // and phone auth needs client-side verified generic invisible reCAPTCHA
        console.log("Phone sign in:", phoneNumber)
        alert("Phone auth requires full Firebase setup with reCAPTCHA.")
    }

    return (
        <div className="bg-card border border-border rounded-xl p-6 shadow-2xl backdrop-blur-sm">
            <div className="space-y-4">
                {/* Google Sign In */}
                <button
                    onClick={handleGoogleSignIn}
                    disabled={loading}
                    className="w-full flex items-center justify-center gap-2 bg-white text-black hover:bg-gray-200 transition-colors py-2.5 rounded-lg font-medium"
                >
                    {loading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                        <svg className="h-4 w-4" viewBox="0 0 24 24">
                            <path
                                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                                fill="#4285F4"
                            />
                            <path
                                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                fill="#34A853"
                            />
                            <path
                                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                                fill="#FBBC05"
                            />
                            <path
                                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                fill="#EA4335"
                            />
                        </svg>
                    )}
                    Continue with Google
                </button>

                <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                        <span className="w-full border-t border-border" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                        <span className="bg-card px-2 text-muted-foreground">Or continue with</span>
                    </div>
                </div>

                {/* Auth Mode Tabs */}
                <div className="flex gap-2">
                    <button
                        onClick={() => setMode("email")}
                        className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-colors ${mode === "email"
                            ? "bg-[#39FF14]/10 text-[#39FF14] border border-[#39FF14]/20"
                            : "bg-secondary text-muted-foreground hover:bg-secondary/80"
                            }`}
                    >
                        Email
                    </button>
                    <button
                        onClick={() => setMode("phone")}
                        className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-colors ${mode === "phone"
                            ? "bg-[#39FF14]/10 text-[#39FF14] border border-[#39FF14]/20"
                            : "bg-secondary text-muted-foreground hover:bg-secondary/80"
                            }`}
                    >
                        Phone
                    </button>
                </div>

                {/* Email Form */}
                {mode === "email" && (
                    <form onSubmit={handleEmailSignIn} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground ml-1">Email</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                <input
                                    type="email"
                                    placeholder="name@example.com"
                                    className="w-full bg-background/50 border border-border rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[#39FF14] placeholder:text-muted-foreground/50"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground ml-1">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                <input
                                    type="password"
                                    placeholder="••••••••"
                                    className="w-full bg-background/50 border border-border rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[#39FF14] placeholder:text-muted-foreground/50"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                        </div>
                        <button className="w-full bg-[#39FF14] text-black font-semibold py-2 rounded-lg hover:bg-[#39FF14]/90 transition-colors">
                            Sign In
                        </button>
                    </form>
                )}

                {/* Phone Form */}
                {mode === "phone" && (
                    <form onSubmit={handlePhoneSignIn} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-muted-foreground ml-1">Phone Number</label>
                            <div className="relative">
                                <Phone className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                <input
                                    type="tel"
                                    placeholder="+1 (555) 000-0000"
                                    className="w-full bg-background/50 border border-border rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[#39FF14] placeholder:text-muted-foreground/50"
                                    value={phoneNumber}
                                    onChange={(e) => setPhoneNumber(e.target.value)}
                                />
                            </div>
                        </div>
                        <button className="w-full bg-[#39FF14] text-black font-semibold py-2 rounded-lg hover:bg-[#39FF14]/90 transition-colors">
                            Send OTP
                        </button>
                        <div id="recaptcha-container"></div>
                    </form>
                )}
            </div>
        </div>
    )
}
