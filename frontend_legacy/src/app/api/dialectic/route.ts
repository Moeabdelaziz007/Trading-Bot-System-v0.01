import { NextResponse } from 'next/server';

// Force dynamic rendering for SSE endpoint
export const dynamic = 'force-dynamic';

// This is a mock implementation for demonstration purposes
// In a real implementation, this would connect to the Cloudflare Worker SSE Endpoint

export async function GET() {
  // Set CORS headers
  const headers = {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  // Create a readable stream
  const stream = new ReadableStream({
    async start(controller) {
      // Send initial connection message
      controller.enqueue(`data: ${JSON.stringify({ type: 'CONNECTED', message: 'Stream connected' })}\n\n`);

      // Simulate sending data periodically
      const interval = setInterval(() => {
        // Randomly send either core or shadow data
        const isCore = Math.random() > 0.5;
        const eventType = isCore ? 'CORE_TOKEN' : 'SHADOW_TOKEN';
        const payload = isCore
          ? `Analyzing market pattern ${Math.floor(Math.random() * 100)}`
          : `Challenging assumption ${Math.floor(Math.random() * 100)}`;

        controller.enqueue(`data: ${JSON.stringify({ type: eventType, payload })}\n\n`);

        // Occasionally send a decision
        if (Math.random() > 0.8) {
          controller.enqueue(`data: ${JSON.stringify({ type: 'DECISION', payload: 'DECISION: LONG 1.5x' })}\n\n`);
        }
      }, 2000);

      // Clean up interval when stream is cancelled
      setTimeout(() => {
        clearInterval(interval);
        controller.close();
      }, 60000); // Close after 1 minute for demo purposes
    },
  });

  return new NextResponse(stream, { headers });
}