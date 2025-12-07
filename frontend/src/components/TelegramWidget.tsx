"use client";
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, MessageCircle, ExternalLink } from 'lucide-react';

interface TelegramMessage {
    id: number;
    type: 'signal' | 'alert' | 'user';
    content: string;
    time: string;
}

const MOCK_MESSAGES: TelegramMessage[] = [
    { id: 1, type: 'signal', content: '🟢 BUY EUR/USD @ 1.0845 | TP: 1.0900 | SL: 1.0820', time: '2m ago' },
    { id: 2, type: 'alert', content: '⚠️ XAU/USD approaching resistance at $2050', time: '15m ago' },
    { id: 3, type: 'user', content: 'Analyze GBP/JPY trend', time: '1h ago' },
];

export default function TelegramWidget() {
    const [message, setMessage] = useState('');

    const handleSend = () => {
        if (!message.trim()) return;
        // TODO: Send to backend -> Telegram
        console.log('Sending to Telegram:', message);
        setMessage('');
    };

    return (
        <div className="bento-card h-full flex flex-col">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <MessageCircle className="w-4 h-4 text-[#0088cc]" />
                    <h3 className="text-sm font-medium text-[var(--text-muted)]">Telegram</h3>
                </div>
                <button className="text-xs text-[var(--neon-cyan)] hover:underline flex items-center gap-1">
                    Open Bot <ExternalLink className="w-3 h-3" />
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 space-y-2 overflow-y-auto max-h-48 mb-4">
                {MOCK_MESSAGES.map((msg, index) => (
                    <motion.div
                        key={msg.id}
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className={`p-2.5 rounded-xl text-xs ${msg.type === 'signal'
                                ? 'bg-[var(--neon-green)]/10 border border-[var(--neon-green)]/20 text-[var(--neon-green)]'
                                : msg.type === 'alert'
                                    ? 'bg-[var(--neon-gold)]/10 border border-[var(--neon-gold)]/20 text-[var(--neon-gold)]'
                                    : 'bg-[var(--surface)] text-white'
                            }`}
                    >
                        <p>{msg.content}</p>
                        <span className="text-[10px] text-[var(--text-dim)] mt-1 block">{msg.time}</span>
                    </motion.div>
                ))}
            </div>

            {/* Quick Reply */}
            <div className="flex gap-2">
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Send command..."
                    className="flex-1 bg-[var(--surface)] border border-[var(--glass-border)] rounded-xl px-3 py-2 text-sm text-white placeholder:text-[var(--text-dim)] focus:outline-none focus:border-[var(--neon-cyan)]"
                />
                <button
                    onClick={handleSend}
                    className="p-2 rounded-xl bg-[#0088cc] hover:bg-[#0088cc]/80 transition-colors"
                >
                    <Send className="w-4 h-4 text-white" />
                </button>
            </div>
        </div>
    );
}
