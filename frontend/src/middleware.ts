import createMiddleware from 'next-intl/middleware';
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

// next-intl middleware for i18n routing
const intlMiddleware = createMiddleware({
    locales: ['en', 'ar'],
    defaultLocale: 'en',
    localePrefix: 'as-needed'
});

// Define which routes are protected by Clerk
const isProtectedRoute = createRouteMatcher([
    '/dashboard(.*)',
    '/profile(.*)',
    '/settings(.*)',
    '/bots(.*)',
    '/test-ai(.*)'
]);

// Export the combined middleware
export default clerkMiddleware((auth, req) => {
    // Protect routes that require authentication
    if (isProtectedRoute(req)) auth().protect();
    
    // Apply internationalization to all routes
    return intlMiddleware(req);
});

export const config = {
    matcher: [
        // Match all request paths except for the ones starting with:
        // - api (API routes)
        // - _next/static (static files)
        // - _next/image (image optimization files)
        // - favicon.ico (favicon file)
        '/((?!api|_next/static|_next/image|favicon.ico).*)',
    ],
};