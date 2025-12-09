"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Wallet, CreditCard, Building2, Check, Loader2, X } from "lucide-react";

interface Provider {
    id: string;
    name: string;
    nameAr: string;
    icon: React.ReactNode;
    color: string;
    connected: boolean;
}

export default function ConnectWallet() {
    const [isOpen, setIsOpen] = useState(false);
    const [connecting, setConnecting] = useState<string | null>(null);

    const [providers, setProviders] = useState<Provider[]>([
        {
            id: "coinbase",
            name: "Coinbase",
            nameAr: "كوين بيس",
            icon: <Wallet className="w-5 h-5" />,
            color: "from-blue-500 to-blue-600",
            connected: false,
        },
        {
            id: "stripe",
            name: "Stripe",
            nameAr: "البطاقة الائتمانية",
            icon: <CreditCard className="w-5 h-5" />,
            color: "from-purple-500 to-purple-600",
            connected: false,
        },
        {
            id: "paypal",
            name: "PayPal",
            nameAr: "باي بال",
            icon: <Building2 className="w-5 h-5" />,
            color: "from-blue-400 to-blue-500",
            connected: false,
        },
    ]);

    const handleConnect = async (providerId: string) => {
        setConnecting(providerId);

        // Simulate OAuth flow - replace with actual implementation
        try {
            // TODO: Call backend OAuth endpoint
            // const response = await fetch(`/api/auth/${providerId}/connect`);

            await new Promise((resolve) => setTimeout(resolve, 2000));

            setProviders((prev) =>
                prev.map((p) =>
                    p.id === providerId ? { ...p, connected: true } : p
                )
            );
        } catch (error) {
            console.error("Connection failed:", error);
        } finally {
            setConnecting(null);
        }
    };

    const handleDisconnect = (providerId: string) => {
        setProviders((prev) =>
            prev.map((p) =>
                p.id === providerId ? { ...p, connected: false } : p
            )
        );
    };

    return (
        <>
            {/* Trigger Button */}
            <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setIsOpen(true)}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg font-medium shadow-lg hover:shadow-emerald-500/25 transition-all"
            >
                <Wallet className="w-4 h-4" />
                <span>ربط المحفظة</span>
            </motion.button>

            {/* Modal */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
                        onClick={() => setIsOpen(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            onClick={(e) => e.stopPropagation()}
                            className="w-full max-w-md bg-slate-900 border border-slate-700 rounded-2xl p-6 shadow-2xl"
                        >
                            {/* Header */}
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xl font-bold text-white">ربط وسيلة الدفع</h2>
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                                >
                                    <X className="w-5 h-5 text-slate-400" />
                                </button>
                            </div>

                            {/* Providers List */}
                            <div className="space-y-3">
                                {providers.map((provider) => (
                                    <div
                                        key={provider.id}
                                        className="flex items-center justify-between p-4 bg-slate-800/50 border border-slate-700 rounded-xl"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div
                                                className={`p-2 rounded-lg bg-gradient-to-br ${provider.color} text-white`}
                                            >
                                                {provider.icon}
                                            </div>
                                            <div>
                                                <p className="font-medium text-white">{provider.name}</p>
                                                <p className="text-sm text-slate-400">{provider.nameAr}</p>
                                            </div>
                                        </div>

                                        {provider.connected ? (
                                            <div className="flex items-center gap-2">
                                                <span className="flex items-center gap-1 text-sm text-emerald-400">
                                                    <Check className="w-4 h-4" />
                                                    متصل
                                                </span>
                                                <button
                                                    onClick={() => handleDisconnect(provider.id)}
                                                    className="text-xs text-slate-500 hover:text-red-400 transition-colors"
                                                >
                                                    قطع
                                                </button>
                                            </div>
                                        ) : (
                                            <motion.button
                                                whileHover={{ scale: 1.05 }}
                                                whileTap={{ scale: 0.95 }}
                                                onClick={() => handleConnect(provider.id)}
                                                disabled={connecting === provider.id}
                                                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                                            >
                                                {connecting === provider.id ? (
                                                    <Loader2 className="w-4 h-4 animate-spin" />
                                                ) : (
                                                    "ربط"
                                                )}
                                            </motion.button>
                                        )}
                                    </div>
                                ))}
                            </div>

                            {/* Footer */}
                            <p className="mt-6 text-xs text-slate-500 text-center">
                                🔒 جميع البيانات مشفرة ومحمية. لا نحتفظ ببياناتك المصرفية.
                            </p>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
