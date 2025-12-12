import { NextRequest, NextResponse } from 'next/server';

/**
 * Coinbase OAuth Callback Handler
 * 
 * This endpoint receives the authorization code from Coinbase after the user
 * authorizes the application. It then exchanges this code for an access token
 * by calling the backend worker.
 */

export async function GET(request: NextRequest) {
    try {
        // Extract authorization code from query parameters
        const { searchParams } = new URL(request.url);
        const code = searchParams.get('code');
        const error = searchParams.get('error');
        
        // Handle OAuth error
        if (error) {
            const errorDescription = searchParams.get('error_description');
            console.error('Coinbase OAuth error:', error, errorDescription);
            return NextResponse.redirect(new URL('/dashboard?oauth_error=' + encodeURIComponent(error), request.url));
        }
        
        // Validate authorization code
        if (!code) {
            console.error('Missing authorization code');
            return NextResponse.redirect(new URL('/dashboard?oauth_error=missing_code', request.url));
        }
        
        // Exchange code for access token via backend worker
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://trading-brain-v1.amrikyy.workers.dev';
        const tokenEndpoint = `${backendUrl}/api/auth/coinbase/callback?code=${encodeURIComponent(code)}`;
        
        // Call backend to handle token exchange and storage
        const response = await fetch(tokenEndpoint);
        const result = await response.json();
        
        if (result.status === 'success') {
            // Redirect to dashboard with success message
            return NextResponse.redirect(new URL('/dashboard?oauth_success=true', request.url));
        } else {
            console.error('Token exchange failed:', result.error);
            return NextResponse.redirect(new URL('/dashboard?oauth_error=' + encodeURIComponent(result.error || 'token_exchange_failed'), request.url));
        }
    } catch (error) {
        console.error('OAuth callback error:', error);
        return NextResponse.redirect(new URL('/dashboard?oauth_error=internal_error', request.url));
    }
}