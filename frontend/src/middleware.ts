import createMiddleware from 'next-intl/middleware';
import { clerkMiddleware } from "@clerk/nextjs/server";

// next-intl middleware for i18n routing
const intlMiddleware = createMiddleware({
    locales: ['en', 'ar'],
    defaultLocale: 'en'
});

// Combine Clerk and next-intl middlewares
export default clerkMiddleware((auth, req) => {
    return intlMiddleware(req);
});

export const config = {
    matcher: [
        // Skip Next.js internals and all static files, unless found in search params
        "/((?!_next|[^?]*\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
        // Always run for API routes
        "/(api|trpc)(.*)",
    ],
};
