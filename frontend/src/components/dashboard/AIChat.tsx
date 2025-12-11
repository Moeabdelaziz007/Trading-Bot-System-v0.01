'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Brain, Loader2, Sparkles, TrendingUp } from 'lucide-react';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

const quickPrompts = [
    { label: 'Analyze Gold', prompt: 'Analyze XAUUSD H1 chart' },
    { label: 'BTC Outlook', prompt: 'What is Bitcoin doing today?' },
    { label: 'Risk Check', prompt: 'Check my portfolio risk' },
    { label: 'Market Sentiment', prompt: 'Current market sentiment?' },
];

export const AIChat: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async (messageText?: string) => {
        const text = messageText || input;
        if (!text.trim() || isLoading) return;

        const userMessage: Message = {
            role: 'user',
            content: text,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text }),
            });

            if (!response.ok) throw new Error('Chat request failed');

            const data = await response.json();

            const assistantMessage: Message = {
                role: 'assistant',
                content: data.response || data.reply || 'No response received.',
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage: Message = {
                role: 'assistant',
                content: '⚠️ Connection error. Please try again.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        sendMessage();
    };

    return (
        <div
            data-testid="ai-chat-widget"
            className="flex flex-col h-full bg-[#0A0A1A]/50 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden"
        >
            {/* Header */}
            <div className="flex items-center gap-3 p-4 border-b border-white/10">
                <div className="p-2 bg-[#A855F7]/20 rounded-lg">
                    <Brain className="w-5 h-5 text-[#A855F7]" />
                </div>
                <div>
                    <h3 className="text-sm font-mono font-bold text-white">AI_ANALYST</h3>
                    <p className="text-xs text-gray-500 font-mono">Powered by GLM-4.5</p>
                </div>
                <div className="ml-auto flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-[#22C55E] animate-pulse"></div>
                    <span className="text-xs text-[#22C55E] font-mono">ONLINE</span>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[200px] max-h-[400px]">
                {messages.length === 0 && (
                    <div className="text-center py-8">
                        <Sparkles className="w-12 h-12 text-[#A855F7]/30 mx-auto mb-3" />
                        <p className="text-sm text-gray-500 font-mono">Ask me about markets, analysis, or trading strategies.</p>
                    </div>
                )}

                <AnimatePresence>
                    {messages.map((msg, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[80%] p-3 rounded-lg font-mono text-sm ${msg.role === 'user'
                                        ? 'bg-[#A855F7]/20 text-white border border-[#A855F7]/30'
                                        : 'bg-[#1A1A2E] text-gray-300 border border-white/10'
                                    }`}
                            >
                                {msg.content}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {isLoading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-2 text-gray-400"
                    >
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-xs font-mono">Analyzing...</span>
                    </motion.div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Quick Prompts */}
            <div className="px-4 py-2 border-t border-white/5">
                <div className="flex gap-2 overflow-x-auto pb-2">
                    {quickPrompts.map((qp, idx) => (
                        <button
                            key={idx}
                            onClick={() => sendMessage(qp.prompt)}
                            disabled={isLoading}
                            data-testid={`quick-prompt-${idx}`}
                            className="flex-shrink-0 px-3 py-1.5 bg-[#A855F7]/10 border border-[#A855F7]/20 rounded-lg text-xs font-mono text-[#A855F7] hover:bg-[#A855F7]/20 transition-colors disabled:opacity-50"
                        >
                            {qp.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Input Area */}
            <form onSubmit={handleSubmit} className="p-4 border-t border-white/10">
                <div className="flex gap-2">
                    <div className="flex-1 relative">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#A855F7] font-mono">&gt;</span>
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask the AI Analyst..."
                            disabled={isLoading}
                            data-testid="chat-input"
                            className="w-full bg-[#050505] border border-white/10 rounded-lg pl-8 pr-4 py-3 text-white font-mono text-sm placeholder-gray-600 focus:outline-none focus:border-[#A855F7]/50 disabled:opacity-50"
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        data-testid="chat-send-button"
                        className="px-4 py-3 bg-[#A855F7] hover:bg-[#9333EA] disabled:bg-gray-600 rounded-lg transition-colors disabled:cursor-not-allowed"
                    >
                        {isLoading ? (
                            <Loader2 className="w-5 h-5 text-white animate-spin" />
                        ) : (
                            <Send className="w-5 h-5 text-white" />
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default AIChat;
