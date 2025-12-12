import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

// Backend URL - deployed to Cloudflare Workers
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://trading-brain-v1.amrikyy1.workers.dev';

export async function POST(request: Request) {
    try {
        const { prompt, model } = await request.json();

        // Try to call real backend first
        try {
            const backendResponse = await fetch(`${BACKEND_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: prompt,
                    model: model || 'glm-4.5',
                    context: 'trading_analysis'
                }),
            });

            if (backendResponse.ok) {
                const data = await backendResponse.json();

                return NextResponse.json({
                    success: true,
                    analysis: data.response || data.message || data.analysis,
                    metrics: {
                        confidence: data.confidence || 78,
                        risk_level: data.risk_level || 'Medium',
                        execution_time: data.latency || '1.2s'
                    },
                    source: 'live_backend'
                });
            }
        } catch (backendError) {
            console.log('Backend unavailable, using fallback:', backendError);
        }

        // Fallback: Return intelligent mock response
        const symbol = prompt.includes('EUR') ? 'EURUSD' : prompt.includes('XAU') ? 'XAUUSD' : prompt.includes('USD') ? 'USDJPY' : 'Unknown';
        const direction = prompt.toLowerCase().includes('long') ? 'LONG' : prompt.toLowerCase().includes('short') ? 'SHORT' : 'HOLD';

        const mockAnalysis = `
### 🧠 GLM-4.5 Analysis (Fallback Mode)

**Symbol:** ${symbol}
**Requested Direction:** ${direction}

#### 📊 Technical Analysis
- **Trend (H1):** ${Math.random() > 0.5 ? 'Bullish' : 'Bearish'}
- **AEXI Score:** ${Math.floor(60 + Math.random() * 30)}/100
- **Dream Score:** ${Math.floor(50 + Math.random() * 40)}/100

#### 🛡️ Risk Assessment
- **Volatility:** ${Math.random() > 0.5 ? 'High' : 'Moderate'}
- **Key Level:** ${symbol === 'XAUUSD' ? '2650.00' : symbol === 'EURUSD' ? '1.0850' : '150.00'}

#### 🎯 Recommendation
**Action:** ${direction === 'HOLD' ? 'WAIT for clearer signal' : `Consider ${direction} with proper risk management`}

> ⚠️ This is fallback data. Connect backend for live analysis.
        `.trim();

        return NextResponse.json({
            success: true,
            analysis: mockAnalysis,
            metrics: {
                confidence: Math.floor(60 + Math.random() * 25),
                risk_level: Math.random() > 0.5 ? 'High' : 'Medium',
                execution_time: '0.5s'
            },
            source: 'fallback'
        });

    } catch (error) {
        return NextResponse.json({
            success: false,
            error: 'Analysis Failed',
            details: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
}
