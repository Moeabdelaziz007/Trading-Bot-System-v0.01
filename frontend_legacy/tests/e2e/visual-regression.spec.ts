import { test, expect } from '@playwright/test';

test.describe('Visual Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Set consistent viewport for visual tests
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  test('should check dashboard-v2 layout consistency on desktop', async ({ page }) => {
    await page.goto('/en/dashboard-v2');
    
    // Wait for all dynamic content to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Take full page screenshot
    await expect(page).toHaveScreenshot('dashboard-v2-desktop-full.png', {
      fullPage: true,
      animations: 'disabled'
    });
    
    // Take screenshot of key components
    const spiderBrain = page.locator('text=SPIDER_WEB_BRAIN').first();
    if (await spiderBrain.count() > 0) {
      await expect(spiderBrain).toBeVisible();
      await expect(spiderBrain.locator('..')).toHaveScreenshot('spider-brain-component.png', {
        animations: 'disabled'
      });
    }
    
    const twinTurbo = page.locator('text=TWIN_TURBO_ENGINES').first();
    if (await twinTurbo.count() > 0) {
      await expect(twinTurbo).toBeVisible();
      await expect(twinTurbo.locator('..')).toHaveScreenshot('twin-turbo-component.png', {
        animations: 'disabled'
      });
    }
  });

  test('should check dashboard-v2 layout on mobile without CLS issues', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/en/dashboard-v2');
    
    // Wait for initial load
    await page.waitForLoadState('domcontentloaded');
    
    // Take initial screenshot
    await expect(page).toHaveScreenshot('dashboard-v2-mobile-initial.png', {
      fullPage: true,
      animations: 'disabled'
    });
    
    // Wait for dynamic content to load
    await page.waitForTimeout(3000);
    
    // Take final screenshot
    await expect(page).toHaveScreenshot('dashboard-v2-mobile-final.png', {
      fullPage: true,
      animations: 'disabled'
    });
    
    // Check for critical elements visibility
    await expect(page.locator('h1')).toContainText('AXIOM ANTIGRAVITY');
    await expect(page.locator('nav')).toBeVisible();
  });

  test('should check agent-lab layout consistency on desktop', async ({ page }) => {
    await page.goto('/en/agent-lab');
    
    // Wait for all content to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Take full page screenshot
    await expect(page).toHaveScreenshot('agent-lab-desktop-full.png', {
      fullPage: true,
      animations: 'disabled'
    });
    
    // Check three-column layout
    const gridLayout = page.locator('[class*="grid-cols-12"]').first();
    if (await gridLayout.count() > 0) {
      await expect(gridLayout).toHaveScreenshot('agent-lab-grid-layout.png', {
        animations: 'disabled'
      });
    }
  });

  test('should check agent-lab layout on mobile with proper responsive behavior', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/en/agent-lab');
    
    // Wait for content to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Take mobile screenshot
    await expect(page).toHaveScreenshot('agent-lab-mobile-full.png', {
      fullPage: true,
      animations: 'disabled'
    });
    
    // Verify responsive behavior
    await expect(page.locator('h1')).toContainText('AGENT_FOUNDRY');
    
    // Check if layout adapts to single column on mobile
    const mobileGrid = page.locator('[class*="grid-cols-1"]').first();
    const hasMobileLayout = await mobileGrid.count() > 0;
    
    if (hasMobileLayout) {
      await expect(mobileGrid).toBeVisible();
    }
  });

  test('should verify neon glow effects do not cause performance issues', async ({ page }) => {
    await page.goto('/en/dashboard-v2');
    
    // Collect performance metrics
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paint = performance.getEntriesByType('paint');
      
      const firstPaint = paint.find(p => p.name === 'first-paint')?.startTime || 0;
      const firstContentfulPaint = paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0;
      
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint,
        firstContentfulPaint,
        totalResources: performance.getEntriesByType('resource').length
      };
    });
    
    console.log('Performance Metrics:', performanceMetrics);
    
    // Assert performance thresholds
    expect(performanceMetrics.firstContentfulPaint).toBeLessThan(2000);
    expect(performanceMetrics.domContentLoaded).toBeLessThan(3000);
    
    // Check for glow elements
    const glowElements = page.locator('[class*="glow"], [class*="neon"]');
    const glowCount = await glowElements.count();
    
    console.log(`Found ${glowCount} glow/neon elements`);
    expect(glowCount).toBeGreaterThan(0);
    expect(glowCount).toBeLessThan(100); // Reasonable limit
  });

  test('should check for layout shifts during dynamic content loading', async ({ page }) => {
    await page.goto('/en/dashboard-v2');
    
    // Measure initial layout
    const initialLayout = await page.evaluate(() => {
      const main = document.querySelector('main');
      if (!main) return { width: 0, height: 0 };
      return {
        width: main.offsetWidth,
        height: main.offsetHeight
      };
    });
    
    // Wait for dynamic content
    await page.waitForTimeout(3000);
    
    // Measure final layout
    const finalLayout = await page.evaluate(() => {
      const main = document.querySelector('main');
      if (!main) return { width: 0, height: 0 };
      return {
        width: main.offsetWidth,
        height: main.offsetHeight
      };
    });
    
    console.log('Initial layout:', initialLayout);
    console.log('Final layout:', finalLayout);
    
    // Check for significant layout shifts
    const widthShift = Math.abs(initialLayout.width - finalLayout.width);
    const heightShift = Math.abs(initialLayout.height - finalLayout.height);
    
    console.log(`Layout shifts - Width: ${widthShift}px, Height: ${heightShift}px`);
    
    // Allow for reasonable content loading shifts
    expect(widthShift).toBeLessThan(100);
    expect(heightShift).toBeLessThan(200);
  });

  test('should verify agent lab slider interactions do not cause layout shifts', async ({ page }) => {
    await page.goto('/en/agent-lab');
    
    // Wait for sliders to load
    await page.waitForSelector('input[type="range"]', { timeout: 5000 });
    
    // Get initial layout
    const initialSliderLayout = await page.locator('input[type="range"]').first().boundingBox();
    
    if (initialSliderLayout) {
      // Interact with slider
      const firstSlider = page.locator('input[type="range"]').first();
      await firstSlider.fill('75');
      await page.waitForTimeout(500);
      
      // Get layout after interaction
      const finalSliderLayout = await firstSlider.boundingBox();
      
      if (finalSliderLayout) {
        // Check for minimal layout shift
        const xShift = Math.abs(initialSliderLayout.x - finalSliderLayout.x);
        const yShift = Math.abs(initialSliderLayout.y - finalSliderLayout.y);
        
        console.log(`Slider layout shift - X: ${xShift}px, Y: ${yShift}px`);
        
        expect(xShift).toBeLessThan(5);
        expect(yShift).toBeLessThan(5);
      }
    }
  });

  test('should check cross-browser visual consistency', async ({ page, browserName }) => {
    await page.goto('/en/dashboard-v2');
    
    // Wait for content to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Take browser-specific screenshot
    await expect(page).toHaveScreenshot(`dashboard-v2-${browserName}.png`, {
      fullPage: true,
      animations: 'disabled'
    });
    
    // Verify critical elements are visible in all browsers
    await expect(page.locator('h1')).toContainText('AXIOM ANTIGRAVITY');
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('main')).toBeVisible();
  });

  test('should verify responsive breakpoints work correctly', async ({ page }) => {
    const viewports = [
      { width: 1920, height: 1080, name: 'desktop' },
      { width: 1024, height: 768, name: 'tablet' },
      { width: 768, height: 1024, name: 'tablet-portrait' },
      { width: 375, height: 667, name: 'mobile' }
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('/en/dashboard-v2');
      
      // Wait for layout to stabilize
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      // Take screenshot for each viewport
      await expect(page).toHaveScreenshot(`dashboard-v2-${viewport.name}.png`, {
        fullPage: true,
        animations: 'disabled'
      });
      
      // Verify critical elements are visible
      await expect(page.locator('h1')).toContainText('AXIOM ANTIGRAVITY');
      await expect(page.locator('nav')).toBeVisible();
      await expect(page.locator('main')).toBeVisible();
    }
  });

  test('should check for visual consistency after user interactions', async ({ page }) => {
    await page.goto('/en/agent-lab');
    
    // Wait for content to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Take initial screenshot
    await expect(page).toHaveScreenshot('agent-lab-before-interaction.png', {
      fullPage: true,
      animations: 'disabled'
    });
    
    // Perform interactions
    const nameInput = page.locator('input[placeholder*="Alpha Predator"]');
    if (await nameInput.count() > 0) {
      await nameInput.fill('Test Agent');
    }
    
    const sliders = page.locator('input[type="range"]');
    if (await sliders.count() > 0) {
      await sliders.first().fill('80');
    }
    
    await page.waitForTimeout(1000);
    
    // Take screenshot after interactions
    await expect(page).toHaveScreenshot('agent-lab-after-interaction.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should verify color contrast and accessibility', async ({ page }) => {
    await page.goto('/en/dashboard-v2');
    
    // Wait for content to load
    await page.waitForLoadState('networkidle');
    
    // Check for text elements with sufficient contrast
    const textElements = await page.locator('text=/[A-Za-z0-9]/').all();
    
    for (const element of textElements.slice(0, 10)) { // Check first 10 elements
      const styles = await element.evaluate((el) => {
        const computed = window.getComputedStyle(el);
        return {
          color: computed.color,
          backgroundColor: computed.backgroundColor,
          fontSize: computed.fontSize
        };
      });
      
      console.log('Text element styles:', styles);
      
      // Basic check for non-white text on light backgrounds
      expect(styles.color).not.toBe('rgb(255, 255, 255)');
    }
  });
});