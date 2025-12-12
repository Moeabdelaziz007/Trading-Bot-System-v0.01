<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# AlphaAxiom Trading System Frontend

This is the frontend component of the AlphaAxiom Trading System, built with Next.js, Clerk authentication, and real-time market data integration.

## Recent Updates

- Integrated Ably for real-time market data streaming
- Implemented multi-language support (English/Arabic) with RTL layout support
- Added legacy directory to resolve build issues
- Configured Cloudflare Worker proxy for backend API communication
- Set up proper environment variables for deployment
## Run Locally

**Prerequisites:** Node.js (v18 or higher recommended)

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment variables in `.env.local`:
   - Set your Clerk credentials (required for authentication)
   - Configure Ably API key for real-time data
   - Set backend API URL

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser
## Authentication

This application uses Clerk for authentication. The following features are implemented:

- User sign up and sign in
- Protected routes that require authentication
- User profile management
- Session management

### Protected Routes

The following routes require authentication:

- `/dashboard/*`
- `/profile/*`
- `/settings/*`
- `/bots/*`
- `/test-ai/*`

### Environment Variables

To run this application, you need to configure the following environment variables in your `.env.local` file:

```bash
# Clerk Authentication (required)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_YOUR_ACTUAL_PUBLISHABLE_KEY
CLERK_SECRET_KEY=sk_live_YOUR_ACTUAL_SECRET_KEY

# Clerk Redirect URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# Backend API Configuration
NEXT_PUBLIC_API_URL=https://your-worker-url.workers.dev

# System Authentication Key (for protected endpoints)
NEXT_PUBLIC_SYSTEM_KEY=your-system-key-here

# Application Environment
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_LOG_LEVEL=debug
```

**Important:** Replace the placeholder values with your actual Clerk credentials and backend API URL.
## API Routes

API routes are protected using Clerk's authentication:

- `/api/user` - Returns user information (requires authentication)
- `/api/proxy/*` - Proxies requests to backend services (requires authentication for non-public endpoints)

## Real-time Data Integration

This application integrates with Ably for real-time market data streaming:

- Real-time price feeds
- Live trading updates
- Market data streaming with WebSocket connections

## Deployment

This application is designed for deployment on Vercel with the following considerations:

- Environment variables must be configured in Vercel dashboard
- The application requires a backend Cloudflare Worker for API proxying
- Legacy directory is required for successful builds
- Multi-language support (English/Arabic) with RTL layout support

## Troubleshooting

If you encounter the "Publishable key not valid" error:

1. Ensure you have valid Clerk credentials in your `.env.local` file
2. Verify that the `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` starts with `pk_live_` or `pk_test_`
3. Check that there are no extra spaces or characters in the key
4. Restart the development server after updating environment variables
