/**
 * AXIOM Learning Loop - Integration Test Suite
 * 
 * This test suite verifies the complete data flow of the learning loop system.
 */

interface TestResult {
  name: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: number;
  error?: string;
}

interface TestSuiteResult {
  total: number;
  passed: number;
  failed: number;
  skipped: number;
  duration: number;
  results: TestResult[];
}

/**
 * Test 1: Database Schema Validation
 */
async function testDatabaseSchema(env: any): Promise<TestResult> {
  const start = Date.now();
  
  try {
    // Check if all tables exist
    const tables = [
      'signal_events',
      'signal_outcomes',
      'learning_metrics',
      'weight_history',
      'system_monitoring',
      'telegram_reports',
      'api_audit_log'
    ];
    
    for (const table of tables) {
      const result = await env.DB.prepare(
        `SELECT name FROM sqlite_master WHERE type='table' AND name='${table}'`
      ).first();
      
      if (!result) {
        throw new Error(`Table ${table} not found`);
      }
    }
    
    return {
      name: 'Database Schema Validation',
      status: 'passed',
      duration: Date.now() - start
    };
  } catch (error) {
    return {
      name: 'Database Schema Validation',
      status: 'failed',
      duration: Date.now() - start,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Test 2: Signal Insertion
 */
async function testSignalInsertion(env: any): Promise<TestResult> {
  const start = Date.now();
  
  try {
    const now = Date.now();
    
    // Insert test signal
    await env.DB
      .prepare(`
        INSERT INTO signal_events (
          signal_id, symbol, asset_type, signal_direction, price_at_signal,
          timestamp, confidence_score, momentum_score, rsi_score,
          sentiment_score, volume_score, volatility_score, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `)
      .bind(
        `TEST-${now}`,
        'BTCUSDT',
        'crypto',
        'BUY',
        65000.0,
        now,
        0.85,
        85.0,
        25.0,
        75.0,
        80.0,
        60.0,
        'pending'
      )
      .run();
    
    // Verify insertion
    const result = await env.DB
      .prepare('SELECT * FROM signal_events WHERE signal_id = ?')
      .bind(`TEST-${now}`)
      .first();
    
    if (!result) {
      throw new Error('Signal not found after insertion');
    }
    
    return {
      name: 'Signal Insertion',
      status: 'passed',
      duration: Date.now() - start
    };
  } catch (error) {
    return {
      name: 'Signal Insertion',
      status: 'failed',
      duration: Date.now() - start,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Test 3: Outcome Tracking Logic
 */
async function testOutcomeTracking(env: any): Promise<TestResult> {
  const start = Date.now();
  
  try {
    const now = Date.now();
    
    // Insert test signal from 2 hours ago
    const signalId = `OUTCOME-TEST-${now}`;
    const signalTimestamp = now - (2 * 60 * 60 * 1000); // 2 hours ago
    
    await env.DB
      .prepare(`
        INSERT INTO signal_events (
          signal_id, symbol, asset_type, signal_direction, price_at_signal,
          timestamp, confidence_score, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `)
      .bind(
        signalId,
        'ETHUSDT',
        'crypto',
        'BUY',
        3500.0,
        signalTimestamp,
        0.90,
        'pending'
      )
      .run();
    
    // Simulate outcome tracking
    await env.DB
      .prepare(`
        INSERT INTO signal_outcomes (
          signal_event_id, price_1h_later, return_1h, was_correct_1h,
          price_4h_later, return_4h, was_correct_4h,
          price_24h_later, return_24h, was_correct_24h,
          final_status, updated_at
        ) VALUES (
          (SELECT id FROM signal_events WHERE signal_id = ?),
          ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
      `)
      .bind(
        signalId,
        3600.0,
        2.86,
        1,
        3650.0,
        4.29,
        1,
        3700.0,
        5.71,
        1,
        'complete',
        now
      )
      .run();
    
    // Verify outcome
    const result = await env.DB
      .prepare('SELECT * FROM signal_outcomes WHERE signal_event_id = (SELECT id FROM signal_events WHERE signal_id = ?)')
      .bind(signalId)
      .first();
    
    if (!result) {
      throw new Error('Outcome not found');
    }
    
    if (result.return_1h !== 2.86 || result.return_4h !== 4.29 || result.return_24h !== 5.71) {
      throw new Error('Incorrect return values');
    }
    
    return {
      name: 'Outcome Tracking Logic',
      status: 'passed',
      duration: Date.now() - start
    };
  } catch (error) {
    return {
      name: 'Outcome Tracking Logic',
      status: 'failed',
      duration: Date.now() - start,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Test 4: Metrics Aggregation
 */
async function testMetricsAggregation(env: any): Promise<TestResult> {
  const start = Date.now();
  
  try {
    const now = Date.now();
    
    // Insert test signals and outcomes
    const testSignals = [
      { symbol: 'BTCUSDT', direction: 'BUY', price: 65000, return_1h: 3.5, correct: 1 },
      { symbol: 'BTCUSDT', direction: 'BUY', price: 65000, return_1h: -2.1, correct: 0 },
      { symbol: 'ETHUSDT', direction: 'BUY', price: 3500, return_1h: 5.2, correct: 1 },
      { symbol: 'ETHUSDT', direction: 'SELL', price: 3500, return_1h: -1.8, correct: 1 }
    ];
    
    for (const signal of testSignals) {
      const signalId = `METRICS-TEST-${now}-${Math.random()}`;
      
      await env.DB
        .prepare(`
          INSERT INTO signal_events (
            signal_id, symbol, asset_type, signal_direction, price_at_signal,
            timestamp, confidence_score, status
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `)
        .bind(
          signalId,
          signal.symbol,
          'crypto',
          signal.direction,
          signal.price,
          now,
          0.80,
          'completed'
        )
        .run();
      
      await env.DB
        .prepare(`
          INSERT INTO signal_outcomes (
            signal_event_id, price_1h_later, return_1h, was_correct_1h,
            final_status, updated_at
          ) VALUES (
            (SELECT id FROM signal_events WHERE signal_id = ?),
            ?, ?, ?, ?, ?
          )
        `)
        .bind(
          signalId,
          signal.price * (1 + signal.return_1h / 100),
          signal.return_1h,
          signal.correct,
          'complete',
          now
        )
        .run();
    }
    
    // Calculate metrics
    const result = await env.DB
      .prepare(`
        SELECT 
          symbol,
          signal_direction,
          COUNT(*) as total_signals,
          SUM(was_correct_1h) as correct_signals,
          ROUND(AVG(return_1h), 2) as avg_return,
          ROUND((SUM(was_correct_1h) * 100.0) / COUNT(*), 2) as accuracy
        FROM signal_events se
        JOIN signal_outcomes so ON se.id = so.signal_event_id
        WHERE DATE(se.timestamp / 1000, 'unixepoch') = DATE('now')
        GROUP BY symbol, signal_direction
        ORDER BY accuracy DESC
      `)
      .all();
    
    if (result.results.length === 0) {
      throw new Error('No metrics calculated');
    }
    
    return {
      name: 'Metrics Aggregation',
      status: 'passed',
      duration: Date.now() - start
    };
  } catch (error) {
    return {
      name: 'Metrics Aggregation',
      status: 'failed',
      duration: Date.now() - start,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Test 5: Weight Optimization
 */
async function testWeightOptimization(env: any): Promise<TestResult> {
  const start = Date.now();
  
  try {
    // Test weight storage in KV
    const testWeights = {
      momentum: 0.4,
      rsi: 0.2,
      sentiment: 0.2,
      volume: 0.2,
      volatility: 0.2
    };
    
    await env.KV.put('signal_weights:latest', JSON.stringify({
      weights: testWeights,
      updated_at: Date.now(),
      version: 1
    }));
    
    // Retrieve weights
    const weightsStr = await env.KV.get('signal_weights:latest');
    if (!weightsStr) {
      throw new Error('Weights not stored in KV');
    }
    
    const storedWeights = JSON.parse(weightsStr);
    if (storedWeights.weights.momentum !== testWeights.momentum) {
      throw new Error('Incorrect weights retrieved');
    }
    
    return {
      name: 'Weight Optimization',
      status: 'passed',
      duration: Date.now() - start
    };
  } catch (error) {
    return {
      name: 'Weight Optimization',
      status: 'failed',
      duration: Date.now() - start,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Test 6: API Endpoints
 */
async function testAPIEndpoints(env: any): Promise<TestResult> {
  const start = Date.now();
  
  try {
    // Test health endpoint
    const healthResponse = await fetch('http://localhost:8787/health');
    if (!healthResponse.ok) {
      throw new Error('Health endpoint failed');
    }
    
    const healthData = await healthResponse.json();
    if (healthData.status !== 'healthy') {
      throw new Error('Health check failed');
    }
    
    return {
      name: 'API Endpoints',
      status: 'passed',
      duration: Date.now() - start
    };
  } catch (error) {
    return {
      name: 'API Endpoints',
      status: 'failed',
      duration: Date.now() - start,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Run all tests
 */
export async function runIntegrationTests(env: any): Promise<TestSuiteResult> {
  const start = Date.now();
  const results: TestResult[] = [];
  
  console.log('Running AXIOM Learning Loop Integration Tests...\n');
  
  // Run tests
  results.push(await testDatabaseSchema(env));
  results.push(await testSignalInsertion(env));
  results.push(await testOutcomeTracking(env));
  results.push(await testMetricsAggregation(env));
  results.push(await testWeightOptimization(env));
  results.push(await testAPIEndpoints(env));
  
  // Calculate summary
  const total = results.length;
  const passed = results.filter(r => r.status === 'passed').length;
  const failed = results.filter(r => r.status === 'failed').length;
  const skipped = results.filter(r => r.status === 'skipped').length;
  
  const duration = Date.now() - start;
  
  // Print results
  console.log('Test Results:\n');
  results.forEach(result => {
    const status = result.status === 'passed' ? '✓' : result.status === 'failed' ? '✗' : '-';
    const color = result.status === 'passed' ? '\x1b[32m' : result.status === 'failed' ? '\x1b[31m' : '\x1b[33m';
    console.log(`${color}${status} ${result.name} (${result.duration}ms)\x1b[0m`);
    if (result.error) {
      console.log(`  Error: ${result.error}`);
    }
  });
  
  console.log(`\nSummary: ${passed}/${total} passed, ${failed} failed, ${skipped} skipped (${duration}ms)`);
  
  return {
    total,
    passed,
    failed,
    skipped,
    duration,
    results
  };
}
