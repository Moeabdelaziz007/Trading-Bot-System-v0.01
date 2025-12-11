import { optimizeSignalWeights, handleCron } from './index';

interface Env {
  DB: D1Database;
  KV: KVNamespace;
}

export default {
  async scheduled(controller: ScheduledController, env: Env, ctx: ExecutionContext) {
    console.log('[Cron Trigger] Weight Optimizer scheduled job started');
    
    ctx.waitUntil(
      handleCron(env).catch((error) => {
        console.error('[Cron Trigger] Error in scheduled job:', error);
      })
    );
  },
  
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    
    // Health check endpoint
    if (url.pathname === '/health') {
      return new Response(JSON.stringify({ status: 'healthy', timestamp: Date.now() }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }
    
    return new Response('Weight Optimizer Worker', {
      status: 200,
      headers: { 'Content-Type': 'text/plain' },
    });
  },
};
