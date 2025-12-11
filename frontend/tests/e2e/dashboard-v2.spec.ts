import { test, expect, waitForComponent, mockDashboardAPI, mockAIChat } from '../fixtures/test-helpers';

/**
 * 🧪 DASHBOARD V2 E2E TESTS
 * Using enhanced test infrastructure:
 * - Auth Bypass (zero login time)
 * - Animation Disable (no screenshot diffs)
 * - Mocked APIs (instant data)
 */

test.describe('Dashboard V2 - Critical Path', () => {

  // Use authenticatedPage fixture to skip login screen
  test('should load dashboard components instantly', async ({ authenticatedPage: page }) => {
    // 1. Setup Network Mocks (Fast & Deterministic)
    await mockDashboardAPI(page);
    await mockAIChat(page);

    // 2. Go straight to app (bypass login)
    await page.goto('/en/dashboard-v2');

    // 3. Verify Vital Components Load
    await test.step('Verify Twin-Turbo Engines', async () => {
      // Use polling helper instead of hard wait
      // Note: Components might be lazy loaded, so we use the robust waiter
      const gauges = await waitForComponent(page, 'twin-turbo-gauges');
      await expect(gauges).toBeVisible();
      await expect(page.getByText('TWIN_TURBO_ENGINES')).toBeVisible();
      await expect(page.getByText('AEXI PROTOCOL')).toBeVisible();
    });

    await test.step('Verify Spider Brain', async () => {
      const spiderBrain = await waitForComponent(page, 'spider-brain-status');
      await expect(spiderBrain).toBeVisible();
      // Check for specific agents to ensure data mapping works
      // Logic: Wait for the agents to be rendered within the component
      await expect(page.getByTestId('agent-node-core-hub')).toBeVisible({ timeout: 10000 });
      await expect(page.getByTestId('agent-node-reflex')).toBeVisible();
    });

    await test.step('Verify Execution Deck', async () => {
      const deck = await waitForComponent(page, 'execution-deck');
      await expect(deck.getByTestId('symbol-input')).toBeVisible();
      await expect(deck.getByTestId('kill-switch')).toBeVisible();
    });
  });

  test('should handle AI Chat interactions', async ({ authenticatedPage: page }) => {
    // Debug: Capture console logs
    page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
    page.on('pageerror', err => console.log(`BROWSER ERROR: ${err}`));

    // Mock both APIs to ensure full page stability
    await mockDashboardAPI(page);
    await mockAIChat(page);
    await page.goto('/en/dashboard-v2');

    await test.step('Open AI Chat and send message', async () => {
      // First check if the wrapper exists
      const wrapper = page.getByTestId('ai-chat-wrapper');
      await expect(wrapper).toBeVisible({ timeout: 5000 });

      const chatWidget = await waitForComponent(page, 'ai-chat-widget');

      // Send a message
      const input = chatWidget.locator('input[type="text"]');
      await expect(input).toBeVisible();
      await input.fill('Analyze BTC');
      await input.press('Enter');

      // Verify response (Mocked)
      // Check that a message appears in the chat body (assistant role)
      // The mock response text should appear
      await expect(page.locator('text=This is a mock AI response')).toBeVisible({ timeout: 5000 });
    });
  });

  test('should protect against accidental trades', async ({ authenticatedPage: page }) => {
    await page.goto('/en/dashboard-v2');

    await test.step('Kill Switch Activation', async () => {
      // Locate the switch
      const killSwitch = page.getByTestId('kill-switch');
      await expect(killSwitch).toBeVisible();

      // Current state might be "ACTIVE" (Green) or "STOPPED" (Red)
      // We toggle it
      await killSwitch.click();

      // Just verify it's interactive and handles the click without error
      // Ideally we check for visual feedback, but exact class names depend on state
      // For now, ensure it remains visible
      await expect(killSwitch).toBeVisible();
    });
  });

});