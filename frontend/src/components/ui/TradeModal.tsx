"use client";
import React from 'react';
import { X, AlertTriangle, ArrowRight, Shield, DollarSign } from 'lucide-react';

interface TradeModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    details: { symbol: string; side: string; qty: number; price?: number };
    loading: boolean;
}

export const TradeModal = ({ isOpen, onClose, onConfirm, details, loading }: TradeModalProps) => {
    if (!isOpen) return null;

    const isBuy = details.side.toLowerCase() === 'buy';

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-fade-in">
            {/* Overlay click to close */}
            <div className="absolute inset-0" onClick={onClose}></div>

            {/* Modal Container */}
            <div className="relative w-full max-w-md bg-[#0a0a0a] border border-gray-800 rounded-2xl shadow-2xl overflow-hidden animate-slide-up">

                {/* Header */}
                <div className="p-5 border-b border-gray-800 flex justify-between items-center bg-gradient-to-r from-gray-900/50 to-transparent">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <Shield className="text-cyan-400" size={20} />
                        Confirm Execution
                    </h3>
                    <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors p-1 hover:bg-white/5 rounded-lg">
                        <X size={20} />
                    </button>
                </div>

                {/* Warning Banner */}
                <div className="px-6 py-3 bg-yellow-500/10 border-b border-yellow-500/20 flex items-center gap-2">
                    <AlertTriangle className="text-yellow-500" size={16} />
                    <span className="text-yellow-500 text-xs">Review carefully before confirming</span>
                </div>

                {/* Content */}
                <div className="p-8 text-center">
                    <p className="text-gray-400 text-sm mb-6">You are about to submit the following order:</p>

                    {/* Order Details Visual */}
                    <div className="bg-gradient-to-br from-gray-900/80 to-gray-900/40 p-6 rounded-xl border border-gray-800 mb-6">
                        <div className="flex items-center justify-center gap-3 text-3xl font-mono font-bold">
                            <span className={`px-3 py-1 rounded-lg ${isBuy ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'}`}>
                                {details.side.toUpperCase()}
                            </span>
                            <span className="text-white">{details.qty}</span>
                            <span className="text-gray-500 text-xl">×</span>
                            <span className="text-cyan-400">{details.symbol}</span>
                        </div>
                    </div>

                    {/* Order Summary */}
                    <div className="bg-black/40 p-4 rounded-xl border border-gray-800 space-y-3">
                        <div className="flex justify-between text-sm">
                            <span className="text-gray-500 flex items-center gap-2">
                                <DollarSign size={14} /> Order Type
                            </span>
                            <span className="text-white font-mono">MARKET</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Time in Force</span>
                            <span className="text-white font-mono">DAY</span>
                        </div>
                        <div className="flex justify-between text-sm border-t border-gray-800 pt-3 mt-3">
                            <span className="text-gray-500">Commission</span>
                            <span className="text-emerald-400 font-mono">$0.00</span>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="p-6 border-t border-gray-800 bg-black/30 flex gap-3">
                    <button
                        onClick={onClose}
                        className="flex-1 py-3 rounded-xl border border-gray-700 text-gray-300 hover:bg-gray-800 transition-all font-bold hover:border-gray-600"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={onConfirm}
                        disabled={loading}
                        className={`flex-1 py-3 rounded-xl text-black font-bold transition-all flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 ${isBuy
                            ? 'bg-emerald-500 hover:bg-emerald-400 shadow-emerald-500/30 hover:shadow-emerald-500/50'
                            : 'bg-rose-500 hover:bg-rose-400 shadow-rose-500/30 hover:shadow-rose-500/50'
                            }`}
                    >
                        {loading ? (
                            <span className="animate-spin rounded-full h-5 w-5 border-2 border-black border-t-transparent"></span>
                        ) : (
                            <>
                                Confirm {details.side.toUpperCase()}
                                <ArrowRight size={16} />
                            </>
                        )}
                    </button>
                </div>

            </div>
        </div>
    );
};
