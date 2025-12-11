/**
 * 🧪 PLAYWRIGHT TEST FIXTURES
 * Enhanced test setup for AlphaAxiom E2E testing
 * 
 * Features:
 * 1. Animation disable (visual regression stability)
 * 2. Auth bypass (skip login in every test)
 * 3. Robust selectors (data-testid based)
 */

import { test as base, expect, Page } from '@playwright/test';

// ============================================
// CUSTOM TEST FIXTURE WITH ENHANCEMENTS
// ============================================

export const test = base.extend<{
    authenticatedPage: Page;
}>({
    // Default page with animations disabled
    page: async ({ page }, use) => {
        // Inject CSS to disable all animations and transitions
        await page.addInitScript(() => {
            const style = document.createElement('style');
            style.id = 'playwright-animation-disable';
            style.innerHTML = `
        *, *::before, *::after {
          transition: none !important;
          animation: none !important;
          animation-duration: 0s !important;
          transition-duration: 0s !important;
          caret-color: transparent !important;
        }
        /* Also disable Framer Motion */
        [data-framer-motion] {
          animation: none !important;
          transform: none !important;
        }
      `;
            document.head.appendChild(style);
        });

        // Set a reasonable timeout for all operations
        page.setDefaultTimeout(15000);

        await use(page);
    },

    // Pre-authenticated page (skips login via middleware bypass)
    authenticatedPage: async ({ browser }, use) => {
        // Check if we have stored auth state
        const authFile = 'playwright/.auth/user.json';

        let context;
        try {
            // Try to use existing auth state
            context = await browser.newContext({
                storageState: authFile,
                extraHTTPHeaders: { 'x-e2e-bypass': 'true' }
            });
        } catch {
            // No auth file exists, create new context with bypass header
            context = await browser.newContext({
                extraHTTPHeaders: { 'x-e2e-bypass': 'true' }
            });
        }

        const page = await context.newPage();

        // Inject animation disable CSS
        await page.addInitScript(() => {
            const style = document.createElement('style');
            style.innerHTML = `*, *::before, *::after { transition: none !important; animation: none !important; }`;
            document.head.appendChild(style);
        });

        await use(page);
        await context.close();
    },
});

// ============================================
// CUSTOM MATCHERS & HELPERS
// ============================================

/**
 * Wait for a component to be fully loaded (not just visible)
 * Uses data-testid for reliability
 */
export async function waitForComponent(page: Page, testId: string, timeout = 10000) {
    const locator = page.getByTestId(testId);
    await expect(locator).toBeVisible({ timeout });
    // Additional check: wait for any loading states to complete
    await page.waitForLoadState('networkidle', { timeout });
    return locator;
}

/**
 * Take a stable screenshot (waits for animations to settle)
 */
export async function stableScreenshot(page: Page, name: string) {
    // Wait for network to be idle
    await page.waitForLoadState('networkidle');
    // Small delay to ensure all rendering is complete
    await page.waitForTimeout(100);
    // Take screenshot
    return await page.screenshot({ path: `screenshots/${name}.png`, fullPage: true });
}

/**
 * Mock API response for faster tests
 */
export async function mockDashboardAPI(page: Page) {
    await page.route('**/api/dashboard', async route => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                account: { balance: 100000, equity: 105000 },
                positions: [],
                engines: { aexi: 75, dream: 65, last_signal: null },
                spider_agents: [
                    { id: 'core-hub', status: 'online', latency: 12 },
                    { id: 'reflex', status: 'online', latency: 8 },
                    { id: 'analyst', status: 'online', latency: 45 },
                    { id: 'guardian', status: 'online', latency: 15 },
                    { id: 'collector', status: 'online', latency: 22 },
                    { id: 'journalist', status: 'online', latency: 38 },
                    { id: 'strategist', status: 'online', latency: 52 }
                ],
                timestamp: new Date().toISOString()
            })
        });
    });
}

/**
 * Mock AI Chat for instant responses
 */
export async function mockAIChat(page: Page) {
    await page.route('**/api/chat', async route => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                response: 'This is a mock AI response for testing.',
                source: 'mock',
                model: 'test-model'
            })
        });
    });
}

// ============================================
// AUTH SETUP HELPERS
// ============================================

/**
 * Perform login and save state for reuse
 * Run this in global-setup.ts
 */
export async function setupAuth(page: Page) {
    // Navigate to login
    await page.goto('/login');

    // For Clerk auth, we might need to handle their UI
    // This is a simplified example - adjust for your auth provider

    // Check if already logged in
    const isLoggedIn = await page.locator('[data-testid="user-menu"]').isVisible().catch(() => false);

    if (!isLoggedIn) {
        // Wait for Clerk's sign-in form
        await page.waitForSelector('input[name="identifier"]', { timeout: 5000 }).catch(() => null);

        // Fill in credentials (use environment variables in production)
        await page.fill('input[name="identifier"]', process.env.TEST_USER_EMAIL || 'test@alphaaxiom.com');
        await page.click('button[type="submit"]');

        // Wait for password field and fill
        await page.waitForSelector('input[name="password"]', { timeout: 5000 }).catch(() => null);
        await page.fill('input[name="password"]', process.env.TEST_USER_PASSWORD || 'TestPassword123!');
        await page.click('button[type="submit"]');

        // Wait for redirect to dashboard
        await page.waitForURL('**/', { timeout: 10000 });
    }

    // Save auth state
    await page.context().storageState({ path: 'playwright/.auth/user.json' });
}

// ============================================
// EXPORTS
// ============================================

export { expect } from '@playwright/test';
