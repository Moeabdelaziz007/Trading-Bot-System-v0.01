// Frontend API Client
// ==============================================
// يربط الواجهة بـ Backend (FastAPI)
// ==============================================

const API_BASE = 'https://trading-brain-v1.amrikyy1.workers.dev';
const WS_BASE = 'wss://trading-brain-v1.amrikyy1.workers.dev';

export interface MarketData {
    symbol: string;
    trade_symbol: string;
    price: number;
    open: number;
    high: number;
    low: number;
    change: number;
    change_percent: number;
    volume: number;
    timestamp: string;
    asset_type: string;
}

export interface OrderRequest {
    symbol: string;
    side: 'BUY' | 'SELL';
    amount: number;
    stop_loss?: number;
    take_profit?: number;
    auto_risk?: boolean;
}

export interface SystemStatus {
    sentinel: string;
    jesse: {
        status: string;
        mode: string;
        active_strategies: number;
    };
    tradfi: {
        status: string;
        mode: string;
    };
    active_patterns: number;
    pending_signals: number;
}

// ==============================================
// API FUNCTIONS
// ==============================================

export async function getMarketPrice(symbol: string): Promise<MarketData> {
    const res = await fetch(`${API_BASE}/api/market/${symbol}`);
    if (!res.ok) throw new Error(`Failed to fetch ${symbol}`);
    return res.json();
}

export async function getMarketHistory(symbol: string, period = '1mo', interval = '1d') {
    const res = await fetch(`${API_BASE}/api/market/${symbol}/history?period=${period}&interval=${interval}`);
    if (!res.ok) throw new Error(`Failed to fetch history for ${symbol}`);
    return res.json();
}

export async function getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/api/status`);
    if (!res.ok) throw new Error('Failed to fetch system status');
    return res.json();
}

export async function executeTrade(order: OrderRequest) {
    const res = await fetch(`${API_BASE}/api/trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(order),
    });
    if (!res.ok) throw new Error('Trade execution failed');
    return res.json();
}

export async function getPositions() {
    const res = await fetch(`${API_BASE}/api/positions`);
    if (!res.ok) throw new Error('Failed to fetch positions');
    return res.json();
}

export async function flattenAll() {
    const res = await fetch(`${API_BASE}/api/flatten`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to flatten positions');
    return res.json();
}

export async function getAILogs(limit = 50) {
    const res = await fetch(`${API_BASE}/api/ai/logs?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch AI logs');
    return res.json();
}

export async function analyzeAsset(symbol: string) {
    const res = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol }),
    });
    if (!res.ok) throw new Error('Analysis failed');
    return res.json();
}

// ==============================================
// WEBSOCKET CONNECTION
// ==============================================

export class TradingWebSocket {
    private ws: WebSocket | null = null;
    private reconnectAttempts = 0;
    private maxReconnects = 5;
    private onMessage: (data: any) => void;
    private onStatusChange: (connected: boolean) => void;

    constructor(
        onMessage: (data: any) => void,
        onStatusChange: (connected: boolean) => void
    ) {
        this.onMessage = onMessage;
        this.onStatusChange = onStatusChange;
    }

    connect() {
        try {
            this.ws = new WebSocket(`${WS_BASE}/ws`);

            this.ws.onopen = () => {
                console.log('🔌 WebSocket connected');
                this.reconnectAttempts = 0;
                this.onStatusChange(true);
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.onMessage(data);
                } catch (e) {
                    console.error('Failed to parse WebSocket message', e);
                }
            };

            this.ws.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                this.onStatusChange(false);
                this.attemptReconnect();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
        }
    }

    private attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnects) {
            this.reconnectAttempts++;
            console.log(`Reconnecting... attempt ${this.reconnectAttempts}`);
            setTimeout(() => this.connect(), 2000 * this.reconnectAttempts);
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

// ==============================================
// TRADING API OBJECT (for named imports)
// ==============================================

export const tradingApi = {
    getMarketPrice,
    getMarketHistory,
    getSystemStatus,
    executeTrade,
    getPositions,
    flattenAll,
    getAILogs,
    analyzeAsset,

    // Additional methods for components
    placeOrder: async (order: any) => {
        const res = await fetch(`${API_BASE}/api/trade`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(order),
        });
        if (!res.ok) throw new Error('Order failed');
        return res.json();
    },

    // Chat with AI
    chatWithAI: async (message: string) => {
        const res = await fetch(`${API_BASE}/api/ai/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });
        if (!res.ok) throw new Error('AI chat failed');
        return res.json();
    },

    // Get Dual Brain status
    getBrainStatus: async () => {
        const res = await fetch(`${API_BASE}/api/brain/status`);
        if (!res.ok) throw new Error('Failed to get brain status');
        return res.json();
    }
};

