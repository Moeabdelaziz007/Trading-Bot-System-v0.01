import { NextRequest } from 'next/server';

/**
 * SSE Streaming Endpoint for Dialectic War Room
 * Connects the Python backend to the React frontend
 */

// Simulated dialectic scenarios for demo
const SCENARIOS = [
    {
        condition: "bullish_breakout",
        core: "RSI oversold bounce detected at 28.5. Volume 150% above 20-day average. Breaking key resistance at $95,000. High conviction LONG setup with momentum confirmation.",
        shadow: "WARNING: Thin orderbook liquidity above $95,000. Only 5 BTC visible. High funding rates in perpetuals suggest long squeeze risk. Recent false breakouts at this level.",
        synthesis: "CAUTIOUS_LONG with tight stop at $94,000. Reduce position to 50% normal size until liquidity improves."
    },
    {
        condition: "bearish_divergence",
        core: "Price making higher highs but RSI showing lower highs. Classic bearish divergence pattern. SHORT opportunity with 2.5:1 reward-to-risk ratio.",
        shadow: "Strong spot buying detected on Coinbase. Institutional accumulation ongoing. Divergences can extend for weeks in strong trends. Wait for confirmation.",
        synthesis: "WAIT for price structure break. Set alert at $93,500 support level. No position until confirmation."
    },
    {
        condition: "volatility_expansion",
        core: "Bollinger Bands squeezing tightly. ATR at 30-day low. Volatility expansion imminent. Position for breakout in either direction.",
        shadow: "Low volume compression often leads to false breakouts. Whipsaw probability high. Both longs and shorts getting stopped out.",
        synthesis: "NO_TRADE recommended. Capital preservation mode. Wait for clear directional move with volume."
    }
];

// Sleep utility
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Generate typewriter-style tokens
async function* generateDialecticStream() {
    const scenario = SCENARIOS[Math.floor(Math.random() * SCENARIOS.length)];
    const sessionId = `SESSION_${Date.now()}`;

    // Session Start
    yield formatSSE({
        type: "SESSION_START",
        payload: sessionId,
        timestamp: new Date().toISOString(),
        metadata: { condition: scenario.condition }
    });

    await sleep(500);

    // Calculate scores
    const coreConfidence = 0.7 + Math.random() * 0.25;
    const shadowRegret = 0.3 + Math.random() * 0.4;

    // === CORE PHASE ===
    yield formatSSE({
        type: "PHASE_START",
        payload: "CORE",
        timestamp: new Date().toISOString()
    });

    // Stream Core tokens
    const coreWords = scenario.core.split(' ');
    for (const word of coreWords) {
        yield formatSSE({
            type: "CORE_TOKEN",
            payload: word + " ",
            timestamp: new Date().toISOString(),
            confidence: coreConfidence
        });
        await sleep(40 + Math.random() * 60);
    }

    yield formatSSE({
        type: "PHASE_END",
        payload: "CORE",
        confidence: coreConfidence,
        timestamp: new Date().toISOString()
    });

    await sleep(300);

    // === SHADOW PHASE ===
    yield formatSSE({
        type: "PHASE_START",
        payload: "SHADOW",
        timestamp: new Date().toISOString()
    });

    // Stream Shadow tokens
    const shadowWords = scenario.shadow.split(' ');
    for (const word of shadowWords) {
        yield formatSSE({
            type: "SHADOW_TOKEN",
            payload: word + " ",
            timestamp: new Date().toISOString(),
            confidence: shadowRegret
        });
        await sleep(40 + Math.random() * 60);
    }

    yield formatSSE({
        type: "PHASE_END",
        payload: "SHADOW",
        confidence: shadowRegret,
        timestamp: new Date().toISOString()
    });

    await sleep(500);

    // === SYNTHESIS PHASE ===
    yield formatSSE({
        type: "PHASE_START",
        payload: "SYNTHESIS",
        timestamp: new Date().toISOString()
    });

    const synthWords = scenario.synthesis.split(' ');
    for (const word of synthWords) {
        yield formatSSE({
            type: "SYNTHESIS_TOKEN",
            payload: word + " ",
            timestamp: new Date().toISOString()
        });
        await sleep(60 + Math.random() * 80);
    }

    // Calculate E_score
    const eScore = coreConfidence - (shadowRegret * 1.2);
    const decision = eScore > 0.5 ? "EXECUTE_FULL" :
        eScore > 0.3 ? "EXECUTE_REDUCED" :
            eScore > 0.1 ? "HOLD_WAIT" : "BLOCK_TRADE";

    yield formatSSE({
        type: "DECISION",
        payload: decision,
        timestamp: new Date().toISOString(),
        confidence: Math.max(0, Math.min(1, eScore)),
        metadata: {
            core_confidence: Number(coreConfidence.toFixed(3)),
            shadow_regret: Number(shadowRegret.toFixed(3)),
            e_score: Number(eScore.toFixed(3)),
            condition: scenario.condition
        }
    });

    yield formatSSE({
        type: "SESSION_END",
        payload: sessionId,
        timestamp: new Date().toISOString()
    });
}

function formatSSE(data: Record<string, unknown>): string {
    return `data: ${JSON.stringify(data)}\n\n`;
}

export async function GET(request: NextRequest) {
    const encoder = new TextEncoder();

    const stream = new ReadableStream({
        async start(controller) {
            try {
                for await (const chunk of generateDialecticStream()) {
                    controller.enqueue(encoder.encode(chunk));
                }
                controller.close();
            } catch (error) {
                controller.error(error);
            }
        }
    });

    return new Response(stream, {
        headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
        },
    });
}
