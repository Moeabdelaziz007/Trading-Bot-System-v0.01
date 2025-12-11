import {
  getLearningMetrics,
  getSignalWeights,
  getWeightHistory,
  getLatestReport,
  getSystemStats,
  getTopPerformers,
  getWorstPerformers,
  getMonitoringMetrics
} from './index';

interface Env {
  DB: D1Database;
  KV: KVNamespace;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400'
    };
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // Set CORS headers for all responses
    const headers = new Headers(corsHeaders);
    headers.set('Content-Type', 'application/json');
    
    try {
      // Health check
      if (path === '/health') {
        return new Response(
          JSON.stringify({ status: 'healthy', timestamp: Date.now() }),
          { headers }
        );
      }
      
      // API endpoints
      if (path === '/api/mcp/learning/metrics') {
        const response = await getLearningMetrics(env);
        return new Response(JSON.stringify(response), { headers });
      }
      
      if (path === '/api/mcp/learning/weights') {
        const response = await getSignalWeights(env);
        return new Response(JSON.stringify(response), { headers });
      }
      
      if (path === '/api/mcp/learning/weight-history') {
        const response = await getWeightHistory(env);
        return new Response(JSON.stringify(response), { headers });
      }
      
      if (path === '/api/mcp/learning/report') {
        const response = await getLatestReport(env);
        return new Response(JSON.stringify(response), { headers });
      }
      
      if (path === '/api/mcp/learning/stats') {
        const response = await getSystemStats(env);
        return new Response(JSON.stringify(response), { headers });
      }
      
      if (path === '/api/mcp/learning/top-performers') {
        const response = await getTopPerformers(env);
        return new Response(JSON.stringify(response), { headers });
      }
      
      if (path === '/api/mcp/learning/worst-performers') {
        const response = await getWorstPerformers(env);
        return new Response(JSON.stringify(response), { headers });
      }
      
      if (path === '/api/mcp/learning/monitoring') {
        const response = await getMonitoringMetrics(env);
        return new Response(JSON.stringify(response), { headers });
      }
      
      // Not found
      return new Response(
        JSON.stringify({ success: false, error: 'Endpoint not found', timestamp: Date.now() }),
        { status: 404, headers }
      );
      
    } catch (error) {
      console.error('[API] Error handling request:', error);
      return new Response(
        JSON.stringify({ success: false, error: 'Internal server error', timestamp: Date.now() }),
        { status: 500, headers }
      );
    }
  },
};
