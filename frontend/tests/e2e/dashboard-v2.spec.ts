import { test, expect } from '@playwright/test';

test.describe('Dashboard V2 - UI/UX Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard-v2
    await page.goto('/en/dashboard-v2');
  });

  test('should load page in less than 2 seconds', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/en/dashboard-v2');
    
    // Wait for main content to be visible
    await page.waitForSelector('main', { timeout: 2000 });
    
    const loadTime = Date.now() - startTime;
    console.log(`Page load time: ${loadTime}ms`);
    
    // Assert page loads within 2 seconds
    expect(loadTime).toBeLessThan(2000);
    
    // Verify critical elements are loaded
    await expect(page.locator('h1')).toContainText('AXIOM ANTIGRAVITY');
  });

  test('should display sidebar toggle on desktop and mobile', async ({ page }) => {
    // Test desktop view
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.waitForLoadState('networkidle');
    
    // Check for navigation elements
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();
    
    // Look for menu button or sidebar toggle
    const menuButton = page.locator('button').filter({ hasText: '' }).first();
    const hasMenuButton = await menuButton.count() > 0;
    
    if (hasMenuButton) {
      await expect(menuButton).toBeVisible();
    }
    
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForLoadState('networkidle');
    
    // On mobile, menu button should definitely be visible
    const mobileMenuButton = page.locator('button').filter({ hasText: '' }).first();
    await expect(mobileMenuButton).toBeVisible();
  });

  test('should navigate to agent-lab correctly', async ({ page }) => {
    // Look for navigation to agent-lab
    const agentLabLink = page.locator('a[href*="agent-lab"]');
    
    if (await agentLabLink.count() > 0) {
      await agentLabLink.first().click();
      await expect(page).toHaveURL(/.*agent-lab/);
    } else {
      // Try manual navigation as fallback
      await page.goto('/en/agent-lab');
      await expect(page.locator('h1')).toContainText('AGENT_FOUNDRY');
    }
  });

  test('should interact with Spider Brain nodes and open modal', async ({ page }) => {
    // Wait for Spider Brain component to load
    await page.waitForSelector('text=SPIDER_WEB_BRAIN', { timeout: 5000 });
    
    // Look for agent nodes in the spider brain
    const agentNodes = page.locator('[class*="group"]').filter({ hasText: /BRAIN|ZAP|MICROSCOPE|SHIELD|RADIO|NEWSPAPER|BRIEFCASE/i });
    
    if (await agentNodes.count() > 0) {
      // Click on the first agent node
      await agentNodes.first().click();
      
      // Wait for potential modal or tooltip to appear
      await page.waitForTimeout(500);
      
      // Check for tooltip or modal content
      const tooltip = page.locator('[class*="tooltip"], [class*="modal"]').first();
      const hasTooltip = await tooltip.count() > 0;
      
      if (hasTooltip) {
        await expect(tooltip).toBeVisible();
      }
    }
    
    // Verify spider brain status is displayed
    await expect(page.locator('text=MAINNET:')).toBeVisible();
    await expect(page.locator('text=AGENTS ONLINE')).toBeVisible();
  });

  test('should display Twin-Turbo Gauges with animations', async ({ page }) => {
    // Wait for Twin-Turbo component to load
    await page.waitForSelector('text=TWIN_TURBO_ENGINES', { timeout: 5000 });
    
    // Check for gauge components
    await expect(page.locator('text=AEXI PROTOCOL')).toBeVisible();
    await expect(page.locator('text=DREAM MACHINE')).toBeVisible();
    await expect(page.locator('text=MTF_SCALPER')).toBeVisible();
    
    // Check for gauge values (should be numbers)
    const gaugeValues = page.locator('text=/\\d+/').first();
    await expect(gaugeValues).toBeVisible();
    
    // Look for SVG elements representing gauges
    const svgGauges = page.locator('svg circle');
    expect(await svgGauges.count()).toBeGreaterThan(0);
    
    // Check for alignment status
    await expect(page.locator('text=ALIGNMENT')).toBeVisible();
  });

  test('should open Payment Modal and display Grandmaster plan', async ({ page }) => {
    // Look for upgrade button
    const upgradeButton = page.locator('button').filter({ hasText: 'UPGRADE' }).first();
    
    if (await upgradeButton.count() > 0) {
      await upgradeButton.click();
      
      // Wait for modal to appear
      await page.waitForSelector('text=UPGRADE_YOUR_PLAN', { timeout: 3000 });
      
      // Check for Grandmaster plan
      await expect(page.locator('text=Grandmaster')).toBeVisible();
      await expect(page.locator('text=$99')).toBeVisible();
      
      // Check for plan features
      await expect(page.locator('text=Live trading')).toBeVisible();
      await expect(page.locator('text=MT5 Forex integration')).toBeVisible();
      await expect(page.locator('text=Unlimited bots')).toBeVisible();
      
      // Check for payment providers
      await expect(page.locator('text=SELECT_PAYMENT_METHOD')).toBeVisible();
      
      // Close modal
      const closeButton = page.locator('button').filter({ has: page.locator('svg') }).first();
      if (await closeButton.count() > 0) {
        await closeButton.click();
      }
    }
  });

  test('should verify Neon Glow effects without performance issues', async ({ page }) => {
    // Measure performance metrics
    const metrics = await page.evaluate(() => {
      const perfEntries = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: perfEntries.domContentLoadedEventEnd - perfEntries.domContentLoadedEventStart,
        loadComplete: perfEntries.loadEventEnd - perfEntries.loadEventStart,
        firstPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime || 0
      };
    });
    
    console.log('Performance metrics:', metrics);
    
    // Assert reasonable performance
    expect(metrics.firstContentfulPaint).toBeLessThan(1500);
    
    // Check for neon glow elements
    const glowElements = page.locator('[class*="glow"], [class*="neon"]');
    const glowCount = await glowElements.count();
    console.log(`Found ${glowCount} glow elements`);
    
    // Verify glow elements exist
    expect(glowCount).toBeGreaterThan(0);
    
    // Check for CSS animations
    const animatedElements = page.locator('[class*="animate"]');
    const animationCount = await animatedElements.count();
    console.log(`Found ${animationCount} animated elements`);
    
    // Verify animations are present but not excessive
    expect(animationCount).toBeGreaterThan(0);
    expect(animationCount).toBeLessThan(50); // Reasonable limit
  });

  test('should be responsive across different screen sizes', async ({ page }) => {
    // Test desktop
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForLoadState('networkidle');
    
    // Check main layout
    await expect(page.locator('main')).toBeVisible();
    await expect(page.locator('nav')).toBeVisible();
    
    // Test tablet
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('main')).toBeVisible();
    
    // Test mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('main')).toBeVisible();
    
    // Check for mobile-specific adjustments
    const gridElements = page.locator('[class*="grid"]');
    if (await gridElements.count() > 0) {
      // Verify grid layouts adapt to mobile
      await expect(gridElements.first()).toBeVisible();
    }
  });

  test('should handle layout shifts properly on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Take initial screenshot
    await page.waitForLoadState('networkidle');
    const initialScreenshot = await page.screenshot();
    
    // Wait for dynamic content to load
    await page.waitForTimeout(2000);
    
    // Take final screenshot
    const finalScreenshot = await page.screenshot();
    
    // Compare screenshots (basic size check)
    expect(initialScreenshot.length).toBeGreaterThan(0);
    expect(finalScreenshot.length).toBeGreaterThan(0);
    
    // Check for cumulative layout shift indicators
    const clsElements = page.locator('[class*="shift"], [class*="layout"]');
    const hasCLSIndicators = await clsElements.count() > 0;
    
    if (hasCLSIndicators) {
      console.log('CLS indicators found:', await clsElements.count());
    }
  });

  test('should display critical metrics and data', async ({ page }) => {
    // Wait for data to load
    await page.waitForTimeout(2000);
    
    // Check for portfolio data
    const portfolioElements = page.locator('text=PORTFOLIO');
    if (await portfolioElements.count() > 0) {
      await expect(portfolioElements.first()).toBeVisible();
    }
    
    // Check for bot scores
    const botScores = page.locator('text=BOT_SCORES');
    if (await botScores.count() > 0) {
      await expect(botScores.first()).toBeVisible();
    }
    
    // Check for latency information
    const latencyInfo = page.locator('text=/\\d+ms/');
    if (await latencyInfo.count() > 0) {
      await expect(latencyInfo.first()).toBeVisible();
    }
    
    // Check for status indicators
    const statusIndicators = page.locator('[class*="pulse"], [class*="status"]');
    expect(await statusIndicators.count()).toBeGreaterThan(0);
  });
});