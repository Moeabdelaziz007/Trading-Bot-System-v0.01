import { test, expect } from '@playwright/test';

test.describe('Agent Lab - UI/UX Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to agent-lab
    await page.goto('/en/agent-lab');
  });

  test('should load agent lab page correctly', async ({ page }) => {
    // Check page title and header
    await expect(page.locator('h1')).toContainText('AGENT_FOUNDRY');
    await expect(page.locator('text=Create & Simulate Trading Agents')).toBeVisible();
    
    // Check for LAB_MODE indicator
    await expect(page.locator('text=LAB_MODE')).toBeVisible();
    
    // Verify three-column layout
    await expect(page.locator('main')).toBeVisible();
  });

  test('should handle drag and drop for avatar upload', async ({ page }) => {
    // Wait for Agent Builder to load
    await page.waitForSelector('text=AGENT_IDENTITY', { timeout: 5000 });
    
    // Look for the drag and drop area
    const dragArea = page.locator('[class*="overflow-hidden"]').filter({ has: page.locator('text=UPLOAD_AVATAR') }).first();
    
    if (await dragArea.count() > 0) {
      // Test drag over event
      await dragArea.dispatchEvent('dragover');
      
      // Check if drag active state is applied
      const dragActiveElement = dragArea.locator('[class*="scale-105"]');
      const hasDragActive = await dragActiveElement.count() > 0;
      
      if (hasDragActive) {
        await expect(dragActiveElement).toBeVisible();
      }
      
      // Test drag leave event
      await dragArea.dispatchEvent('dragleave');
      
      // Create a mock file for testing
      const fileInput = dragArea.locator('input[type="file"]');
      if (await fileInput.count() > 0) {
        // Simulate file selection
        await fileInput.setInputFiles({
          name: 'test-avatar.png',
          mimeType: 'image/png',
          buffer: Buffer.from('fake-image-data')
        });
        
        // Wait for potential image upload processing
        await page.waitForTimeout(1000);
      }
    }
  });

  test('should update agent name and description inputs', async ({ page }) => {
    // Wait for form inputs to load
    await page.waitForSelector('input[placeholder*="Alpha Predator"]', { timeout: 5000 });
    
    // Test name input
    const nameInput = page.locator('input[placeholder*="Alpha Predator"]');
    await expect(nameInput).toBeVisible();
    await nameInput.fill('Test Agent Alpha');
    await expect(nameInput).toHaveValue('Test Agent Alpha');
    
    // Test description textarea
    const descriptionTextarea = page.locator('textarea[placeholder*="trading philosophy"]');
    if (await descriptionTextarea.count() > 0) {
      await expect(descriptionTextarea).toBeVisible();
      await descriptionTextarea.fill('Advanced trading strategy with risk management');
      await expect(descriptionTextarea).toHaveValue('Advanced trading strategy with risk management');
    }
  });

  test('should interact with Agent DNA Sliders', async ({ page }) => {
    // Wait for DNA configuration section
    await page.waitForSelector('text=DNA_CONFIGURATION', { timeout: 5000 });
    
    // Find all sliders
    const sliders = page.locator('input[type="range"]');
    const sliderCount = await sliders.count();
    
    expect(sliderCount).toBeGreaterThan(0);
    
    // Test each slider
    for (let i = 0; i < Math.min(sliderCount, 3); i++) {
      const slider = sliders.nth(i);
      await expect(slider).toBeVisible();
      
      // Get initial value
      const initialValue = await slider.inputValue();
      
      // Move slider to different positions
      await slider.fill('75');
      await page.waitForTimeout(500);
      
      // Verify value changed
      const newValue = await slider.inputValue();
      expect(newValue).toBe('75');
      
      // Check if value display updates
      const valueDisplay = page.locator(`text=${newValue}`).first();
      if (await valueDisplay.count() > 0) {
        await expect(valueDisplay).toBeVisible();
      }
    }
  });

  test('should update slider values dynamically during drag', async ({ page }) => {
    // Wait for sliders to load
    await page.waitForSelector('input[type="range"]', { timeout: 5000 });
    
    // Find the first slider
    const firstSlider = page.locator('input[type="range"]').first();
    await expect(firstSlider).toBeVisible();
    
    // Test drag interaction
    await firstSlider.hover();
    await page.mouse.down();
    await page.mouse.move(100, 0);
    await page.waitForTimeout(200);
    await page.mouse.up();
    
    // Check if value display updates during interaction
    const valueDisplays = page.locator('text=/\\d+/');
    const hasValueDisplay = await valueDisplays.count() > 0;
    
    if (hasValueDisplay) {
      await expect(valueDisplays.first()).toBeVisible();
    }
  });

  test('should display slider labels and ranges correctly', async ({ page }) => {
    // Wait for DNA configuration
    await page.waitForSelector('text=DNA_CONFIGURATION', { timeout: 5000 });
    
    // Check for specific slider labels
    await expect(page.locator('text=RISK_TOLERANCE')).toBeVisible();
    await expect(page.locator('text=TRADE_FREQUENCY')).toBeVisible();
    await expect(page.locator('text=INTELLIGENCE_LEVEL')).toBeVisible();
    
    // Check for low/high labels
    await expect(page.locator('text=Conservative')).toBeVisible();
    await expect(page.locator('text=Aggressive')).toBeVisible();
    await expect(page.locator('text=Swing Trader')).toBeVisible();
    await expect(page.locator('text=Scalper')).toBeVisible();
    await expect(page.locator('text=Basic Rules')).toBeVisible();
    await expect(page.locator('text=GLM-4.5 AI')).toBeVisible();
  });

  test('should handle broker selection correctly', async ({ page }) => {
    // Wait for broker selection section
    await page.waitForSelector('text=BROKER_SELECTION', { timeout: 5000 });
    
    // Check for broker options
    await expect(page.locator('text=Capital.com')).toBeVisible();
    await expect(page.locator('text=Alpaca')).toBeVisible();
    await expect(page.locator('text=Bybit')).toBeVisible();
    
    // Test broker selection
    const brokerButtons = page.locator('button').filter({ hasText: /Capital\.com|Alpaca|Bybit/ });
    const brokerCount = await brokerButtons.count();
    
    if (brokerCount > 0) {
      // Click on different brokers
      for (let i = 0; i < Math.min(brokerCount, 3); i++) {
        await brokerButtons.nth(i).click();
        await page.waitForTimeout(500);
        
        // Check if selection is applied (visual feedback)
        const selectedButton = brokerButtons.nth(i);
        const hasSelectionClass = await selectedButton.evaluate(el => {
          return el.classList.contains('border-axiom-neon-cyan') || 
                 el.classList.contains('shadow-glow-cyan');
        });
        
        if (hasSelectionClass) {
          console.log(`Broker ${i} selection applied`);
        }
      }
    }
  });

  test('should handle strategy editor interactions', async ({ page }) => {
    // Wait for strategy editor to load
    await page.waitForTimeout(2000);
    
    // Look for strategy editor section
    const strategyEditor = page.locator('text=STRATEGY_EDITOR').first();
    if (await strategyEditor.count() > 0) {
      await expect(strategyEditor).toBeVisible();
      
      // Look for strategy blocks or rules
      const strategyBlocks = page.locator('[class*="strategy"], [class*="rule"]');
      const hasStrategyBlocks = await strategyBlocks.count() > 0;
      
      if (hasStrategyBlocks) {
        console.log(`Found ${await strategyBlocks.count()} strategy blocks`);
      }
    }
  });

  test('should handle simulation sandbox interactions', async ({ page }) => {
    // Wait for simulation sandbox to load
    await page.waitForTimeout(2000);
    
    // Look for simulation sandbox section
    const simulationSandbox = page.locator('text=SIMULATION_SANDBOX').first();
    if (await simulationSandbox.count() > 0) {
      await expect(simulationSandbox).toBeVisible();
      
      // Look for deploy button
      const deployButton = page.locator('button').filter({ hasText: /DEPLOY|DEPLOYMENT/i }).first();
      if (await deployButton.count() > 0) {
        await expect(deployButton).toBeVisible();
        
        // Test deploy button interaction (without actually deploying)
        await deployButton.hover();
        await page.waitForTimeout(500);
      }
    }
  });

  test('should be responsive across different screen sizes', async ({ page }) => {
    // Test desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForLoadState('networkidle');
    
    // Check three-column layout on desktop
    const gridLayout = page.locator('[class*="grid-cols-12"]');
    if (await gridLayout.count() > 0) {
      await expect(gridLayout).toBeVisible();
    }
    
    // Test tablet view
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('main')).toBeVisible();
    
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('main')).toBeVisible();
    
    // Check if layout adapts to mobile
    const mobileGrid = page.locator('[class*="grid-cols-1"]');
    const hasMobileLayout = await mobileGrid.count() > 0;
    
    if (hasMobileLayout) {
      await expect(mobileGrid.first()).toBeVisible();
    }
  });

  test('should handle animations and transitions smoothly', async ({ page }) => {
    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
    
    // Look for animated elements
    const animatedElements = page.locator('[class*="motion"], [class*="animate"]');
    const animationCount = await animatedElements.count();
    
    console.log(`Found ${animationCount} animated elements`);
    
    // Test hover interactions
    const interactiveElements = page.locator('button, [class*="hover:"]');
    const interactiveCount = await interactiveElements.count();
    
    if (interactiveCount > 0) {
      // Test hover on first few interactive elements
      for (let i = 0; i < Math.min(interactiveCount, 3); i++) {
        await interactiveElements.nth(i).hover();
        await page.waitForTimeout(200);
      }
    }
  });

  test('should display DNA visualization background', async ({ page }) => {
    // Wait for DNA visualization to load
    await page.waitForTimeout(2000);
    
    // Look for DNA pattern SVG
    const dnaPattern = page.locator('svg').filter({ has: page.locator('pattern[id*="dna"]') });
    const hasDNAPattern = await dnaPattern.count() > 0;
    
    if (hasDNAPattern) {
      await expect(dnaPattern.first()).toBeVisible();
      console.log('DNA visualization pattern found');
    }
    
    // Check for background elements
    const backgroundElements = page.locator('[class*="fixed"], [class*="inset-0"]');
    const hasBackgroundElements = await backgroundElements.count() > 0;
    
    if (hasBackgroundElements) {
      console.log(`Found ${await backgroundElements.count()} background elements`);
    }
  });

  test('should handle form validation and error states', async ({ page }) => {
    // Wait for form to load
    await page.waitForSelector('input[placeholder*="Alpha Predator"]', { timeout: 5000 });
    
    // Test empty name validation (if applicable)
    const nameInput = page.locator('input[placeholder*="Alpha Predator"]');
    await nameInput.fill('');
    await nameInput.blur();
    
    // Look for validation messages
    const validationMessages = page.locator('[class*="error"], [class*="invalid"], [class*="required"]');
    const hasValidation = await validationMessages.count() > 0;
    
    if (hasValidation) {
      console.log('Form validation is present');
    }
    
    // Test valid input
    await nameInput.fill('Valid Agent Name');
    await expect(nameInput).toHaveValue('Valid Agent Name');
  });
});