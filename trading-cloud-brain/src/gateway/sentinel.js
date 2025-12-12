/**
 * 🛡️ SENTINEL GATEKEEPER - AlphaAPI Gateway
 * The Edge Guard for AlphaAxiom Signal Distribution
 * 
 * Routes:
 *   POST /api/v1/signals/push   - Internal: Receives signals from Decision Engine
 *   GET  /api/v1/signals/latest - External: Clients fetch latest signal
 *   GET  /api/v1/health         - Health check
 * 
 * Security:
 *   - Internal routes: X-Internal-Token validation
 *   - External routes: X-API-Key validation + Rate Limiting
 */

export default {
    async fetch(request, env, ctx) {
        const url = new URL(request.url);
        const path = url.pathname;

        // CORS Headers for client access
        const corsHeaders = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-API-Key, X-Internal-Token",
            "Content-Type": "application/json"
        };

        // Handle preflight
        if (request.method === "OPTIONS") {
            return new Response(null, { headers: corsHeaders });
        }

        // ════════════════════════════════════════════════════════════════
        // ROUTE: Health Check
        // ════════════════════════════════════════════════════════════════
        if (path === "/api/v1/health") {
            return new Response(JSON.stringify({
                status: "healthy",
                service: "AlphaAPI Sentinel Gateway",
                timestamp: new Date().toISOString()
            }), { status: 200, headers: corsHeaders });
        }

        // ════════════════════════════════════════════════════════════════
        // ROUTE: Push Signal (Internal - from Decision Engine)
        // ════════════════════════════════════════════════════════════════
        if (path === "/api/v1/signals/push" && request.method === "POST") {
            // Validate Internal Token
            const token = request.headers.get("X-Internal-Token");
            if (!token || token !== env.INTERNAL_SECRET) {
                return new Response(JSON.stringify({ error: "Forbidden" }), {
                    status: 403, headers: corsHeaders
                });
            }

            try {
                const signal = await request.json();

                // Add server timestamp
                signal.server_timestamp = new Date().toISOString();

                // Store in KV (latest signal)
                await env.SIGNALS_KV.put("signal:latest", JSON.stringify(signal));

                // Also store in history (last 100 signals)
                const historyKey = `signal:${Date.now()}`;
                await env.SIGNALS_KV.put(historyKey, JSON.stringify(signal), {
                    expirationTtl: 86400 // 24 hours
                });

                console.log(`📡 Signal stored: ${signal.action} ${signal.symbol}`);

                return new Response(JSON.stringify({
                    status: "stored",
                    signal_id: signal.signal_id || historyKey
                }), { status: 200, headers: corsHeaders });

            } catch (e) {
                return new Response(JSON.stringify({ error: "Invalid JSON" }), {
                    status: 400, headers: corsHeaders
                });
            }
        }

        // ════════════════════════════════════════════════════════════════
        // ROUTE: Get Latest Signal (External - for Clients)
        // ════════════════════════════════════════════════════════════════
        if (path === "/api/v1/signals/latest" && request.method === "GET") {
            // Validate Client API Key
            const apiKey = request.headers.get("X-API-Key");
            if (!apiKey) {
                return new Response(JSON.stringify({ error: "API Key required" }), {
                    status: 401, headers: corsHeaders
                });
            }

            // Check API Key in KV
            const clientData = await env.API_KEYS_KV.get(apiKey);
            if (!clientData) {
                return new Response(JSON.stringify({ error: "Invalid API Key" }), {
                    status: 401, headers: corsHeaders
                });
            }

            // Rate Limiting (if binding exists)
            if (env.RATE_LIMITER) {
                const { success } = await env.RATE_LIMITER.limit({ key: apiKey });
                if (!success) {
                    return new Response(JSON.stringify({
                        error: "Rate limit exceeded",
                        retry_after: 1
                    }), { status: 429, headers: corsHeaders });
                }
            }

            // Fetch latest signal
            const signal = await env.SIGNALS_KV.get("signal:latest");

            if (!signal) {
                return new Response(JSON.stringify({
                    status: "no_signal",
                    message: "No signals available"
                }), { status: 200, headers: corsHeaders });
            }

            return new Response(signal, { status: 200, headers: corsHeaders });
        }

        // ════════════════════════════════════════════════════════════════
        // ROUTE: List Client's API Keys (Admin)
        // ════════════════════════════════════════════════════════════════
        if (path === "/api/v1/admin/keys" && request.method === "POST") {
            const token = request.headers.get("X-Internal-Token");
            if (!token || token !== env.INTERNAL_SECRET) {
                return new Response(JSON.stringify({ error: "Forbidden" }), {
                    status: 403, headers: corsHeaders
                });
            }

            const { action, api_key, client_name, tier } = await request.json();

            if (action === "create") {
                // Generate new API key if not provided
                const newKey = api_key || `aa-${crypto.randomUUID().slice(0, 16)}`;
                await env.API_KEYS_KV.put(newKey, JSON.stringify({
                    client_name: client_name || "Unknown",
                    tier: tier || "free",
                    created_at: new Date().toISOString()
                }));

                return new Response(JSON.stringify({
                    status: "created",
                    api_key: newKey
                }), { status: 200, headers: corsHeaders });
            }

            if (action === "revoke" && api_key) {
                await env.API_KEYS_KV.delete(api_key);
                return new Response(JSON.stringify({ status: "revoked" }), {
                    status: 200, headers: corsHeaders
                });
            }

            return new Response(JSON.stringify({ error: "Invalid action" }), {
                status: 400, headers: corsHeaders
            });
        }

        // 404 for all other routes
        return new Response(JSON.stringify({ error: "Not Found" }), {
            status: 404, headers: corsHeaders
        });
    }
};
