import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';
import crypto from 'crypto';

/**
 * 🔒 Fort Knox Proxy
 * 
 * This route proxies all API requests to our Cloudflare Workers.
 * The X-System-Key is NEVER exposed to the client.
 * 
 * Flow:
 * 1. User makes request to /api/proxy/trading/dashboard
 * 2. This proxy validates Clerk session
 * 3. Signs request with HMAC
 * 4. Forwards to router-worker
 * 5. Returns response to user
 */

const BACKEND_URL = process.env.CLOUDFLARE_WORKER_URL || 'https://axiom-router.amrikyy1.workers.dev';
const PROXY_SECRET = process.env.PROXY_SECRET || '';

function createSignature(timestamp: number): string {
    return crypto
        .createHmac('sha256', PROXY_SECRET)
        .update(timestamp.toString())
        .digest('hex');
}

export async function GET(
    request: NextRequest,
    { params }: { params: { path: string[] } }
) {
    return handleRequest(request, params.path, 'GET');
}

export async function POST(
    request: NextRequest,
    { params }: { params: { path: string[] } }
) {
    return handleRequest(request, params.path, 'POST');
}

async function handleRequest(
    request: NextRequest,
    pathSegments: string[],
    method: string
) {
    try {
        // 1. Check Clerk session
        const { userId } = await auth();

        // For public endpoints, allow without auth
        const publicPaths = ['status', 'health'];
        const isPublic = publicPaths.some(p => pathSegments.includes(p));

        if (!userId && !isPublic) {
            return NextResponse.json(
                { error: 'Unauthorized', message: 'Please sign in to access this resource' },
                { status: 401 }
            );
        }

        // 2. Create signature
        const timestamp = Date.now();
        const signature = createSignature(timestamp);

        // 3. Build backend URL
        const path = pathSegments.join('/');
        const url = new URL(request.url);
        const queryString = url.search;
        const backendUrl = `${BACKEND_URL}/api/${path}${queryString}`;

        // 4. Forward request
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
            'X-Proxy-Signature': signature,
            'X-Proxy-Timestamp': timestamp.toString(),
            'X-Proxy-User-Id': userId || 'anonymous',
        };

        const fetchOptions: RequestInit = {
            method,
            headers,
        };

        // Include body for POST requests
        if (method === 'POST') {
            const body = await request.text();
            if (body) {
                fetchOptions.body = body;
            }
        }

        const response = await fetch(backendUrl, fetchOptions);
        const data = await response.json();

        // 5. Return response
        return NextResponse.json(data, { status: response.status });

    } catch (error) {
        console.error('Proxy error:', error);
        return NextResponse.json(
            { error: 'Proxy Error', message: 'Failed to reach backend' },
            { status: 502 }
        );
    }
}
