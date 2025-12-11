import { D1Database } from '@cloudflare/d1';
import { KVNamespace } from '@cloudflare/workers-types';

interface Env {
  DB: D1Database;
  KV: KVNamespace;
}

interface SignalWeights {
  momentum: number;
  rsi: number;
  sentiment: number;
  volume: number;
  volatility: number;
}

interface WeightHistory {
  version: number;
  weights: SignalWeights;
  total_signals_analyzed: number;
  accuracy_improvement: number;
  created_at: number;
}

interface FactorPerformance {
  factor: string;
  accuracy: number;
  signal_count: number;
}

/**
 * Get current signal weights from KV
 */
async function getCurrentWeights(kv: KVNamespace): Promise<SignalWeights> {
  const weightsStr = await kv.get('signal_weights:latest');
  
  if (weightsStr) {
    const data = JSON.parse(weightsStr);
    return data.weights;
  }
  
  // Default weights
  return {
    momentum: 0.4,
    rsi: 0.2,
    sentiment: 0.2,
    volume: 0.2,
    volatility: 0.2
  };
}

/**
 * Analyze factor performance over last 30 days
 */
async function analyzeFactorPerformance(db: D1Database): Promise<Array<FactorPerformance>> {
  const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
  
  console.log('[Weight Optimizer] Analyzing factor performance over last 30 days');
  
  const factors = [
    { name: 'momentum', scoreField: 'momentum_score', threshold: 70 },
    { name: 'rsi', scoreField: 'rsi_score', threshold: 30 },
    { name: 'sentiment', scoreField: 'sentiment_score', threshold: 70 },
    { name: 'volume', scoreField: 'volume_score', threshold: 70 },
    { name: 'volatility', scoreField: 'volatility_score', threshold: 50 }
  ];
  
  const performance: Array<FactorPerformance> = [];
  
  for (const factor of factors) {
    const query = `
      SELECT 
        COUNT(*) as total_signals,
        SUM(CASE WHEN so.was_correct_1h = 1 THEN 1 ELSE 0 END) as correct_signals
      FROM signal_events se
      JOIN signal_outcomes so ON se.id = so.signal_event_id
      WHERE se.timestamp > ?
        AND se.${factor.scoreField} >= ${factor.threshold}
        AND so.was_correct_1h IS NOT NULL
    `;
    
    const result = await db.prepare(query).bind(thirtyDaysAgo).first();
    
    if (result.total_signals > 0) {
      const accuracy = (result.correct_signals / result.total_signals) * 100;
      performance.push({
        factor: factor.name,
        accuracy,
        signal_count: result.total_signals
      });
    }
  }
  
  console.log('[Weight Optimizer] Analyzed', performance.length, 'factors');
  return performance;
}

/**
 * Calculate optimal weights based on factor performance
 */
function calculateOptimalWeights(
  currentWeights: SignalWeights,
  factorPerformance: Array<FactorPerformance>
): SignalWeights {
  const newWeights: SignalWeights = { ...currentWeights };
  
  // Adjust weights based on accuracy
  for (const perf of factorPerformance) {
    const factor = perf.factor;
    const accuracy = perf.accuracy;
    
    if (accuracy > 60) {
      // Performing well, increase weight
      newWeights[factor as keyof SignalWeights] *= 1.1;
    } else if (accuracy < 45) {
      // Performing poorly, decrease weight
      newWeights[factor as keyof SignalWeights] *= 0.9;
    }
  }
  
  // Apply safeguards
  const minWeight = 0.05;
  const maxChange = 0.2; // 20% max change
  
  // Normalize weights to sum to 1.0
  const total = Object.values(newWeights).reduce((sum, w) => sum + w, 0);
  const normalizedWeights: SignalWeights = {
    momentum: Math.max(minWeight, newWeights.momentum / total),
    rsi: Math.max(minWeight, newWeights.rsi / total),
    sentiment: Math.max(minWeight, newWeights.sentiment / total),
    volume: Math.max(minWeight, newWeights.volume / total),
    volatility: Math.max(minWeight, newWeights.volatility / total)
  };
  
  // Ensure no factor exceeds 20% change from original
  for (const key in normalizedWeights) {
    const original = currentWeights[key as keyof SignalWeights];
    const current = normalizedWeights[key as keyof SignalWeights];
    const change = Math.abs(current - original) / original;
    
    if (change > maxChange) {
      normalizedWeights[key as keyof SignalWeights] = 
        original + (current - original) * (maxChange / change);
    }
  }
  
  // Final normalization
  const finalTotal = Object.values(normalizedWeights).reduce((sum, w) => sum + w, 0);
  return {
    momentum: normalizedWeights.momentum / finalTotal,
    rsi: normalizedWeights.rsi / finalTotal,
    sentiment: normalizedWeights.sentiment / finalTotal,
    volume: normalizedWeights.volume / finalTotal,
    volatility: normalizedWeights.volatility / finalTotal
  };
}

/**
 * Store new weights in KV with version history
 */
async function storeWeights(
  kv: KVNamespace,
  weights: SignalWeights,
  totalSignalsAnalyzed: number,
  accuracyImprovement: number
): Promise<number> {
  const now = Date.now();
  
  // Get latest version
  const latestVersionStr = await kv.get('signal_weights:latest_version');
  const latestVersion = latestVersionStr ? parseInt(latestVersionStr) : 0;
  const newVersion = latestVersion + 1;
  
  // Store in KV
  await kv.put('signal_weights:latest', JSON.stringify({
    weights,
    updated_at: now,
    based_on_signals: totalSignalsAnalyzed,
    version: newVersion
  }));
  
  await kv.put('signal_weights:latest_version', newVersion.toString());
  
  console.log('[Weight Optimizer] Stored weights version', newVersion);
  
  return newVersion;
}

/**
 * Store weight history in D1
 */
async function storeWeightHistory(
  db: D1Database,
  version: number,
  weights: SignalWeights,
  totalSignalsAnalyzed: number,
  accuracyImprovement: number
): Promise<void> {
  const now = Date.now();
  
  await db
    .prepare(`
      INSERT INTO weight_history (
        version, weights, total_signals_analyzed, accuracy_improvement, created_at
      ) VALUES (?, ?, ?, ?, ?)
    `)
    .bind(
      version,
      JSON.stringify(weights),
      totalSignalsAnalyzed,
      accuracyImprovement,
      now
    )
    .run();
  
  console.log('[Weight Optimizer] Stored weight history version', version);
}

/**
 * Generate optimization report
 */
function formatOptimizationReport(
  currentWeights: SignalWeights,
  newWeights: SignalWeights,
  version: number,
  totalSignalsAnalyzed: number,
  accuracyImprovement: number
): string {
  const emoji = {
    brain: '🧠',
    chart: '📈',
    info: '📊',
    target: '🎯',
    calendar: '📅'
  };
  
  const changes = Object.entries(newWeights).map(([factor, newWeight]) => {
    const currentWeight = currentWeights[factor as keyof SignalWeights];
    const changePct = ((newWeight - currentWeight) / currentWeight * 100).toFixed(1);
    const changeSymbol = newWeight > currentWeight ? '→' : '←';
    return `• ${factor}: ${currentWeight.toFixed(2)} ${changeSymbol} ${newWeight.toFixed(2)} (${changePct}% change)`;
  }).join('\n');
  
  return `${emoji.brain} Weekly Optimization Complete

${emoji.chart} Weight Adjustments:
${changes}

${emoji.info} Based on: ${totalSignalsAnalyzed} signals analyzed
${emoji.target} Expected accuracy improvement: ${accuracyImprovement.toFixed(1)}%

${emoji.calendar} Next optimization: ${new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toLocaleDateString()}`;
}

/**
 * Send optimization report to Telegram
 */
async function sendOptimizationReport(env: Env, report: string): Promise<void> {
  const telegramBotToken = await env.KV.get('TELEGRAM_BOT_TOKEN');
  const telegramChatId = await env.KV.get('TELEGRAM_CHAT_ID');
  
  if (!telegramBotToken || !telegramChatId) {
    console.warn('[Weight Optimizer] Telegram credentials not configured');
    return;
  }
  
  try {
    const url = `https://api.telegram.org/bot${telegramBotToken}/sendMessage`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        chat_id: telegramChatId,
        text: report,
        parse_mode: 'Markdown',
      }),
    });
    
    if (response.ok) {
      console.log('[Weight Optimizer] Optimization report sent to Telegram');
      
      // Store in database
      const now = Date.now();
      await env.DB
        .prepare(`
          INSERT INTO telegram_reports (report_type, report_date, report_content, sent_at, created_at)
          VALUES (?, ?, ?, ?, ?)
        `)
        .bind('weekly', new Date().toISOString().split('T')[0], report, now, now)
        .run();
    }
  } catch (error) {
    console.error('[Weight Optimizer] Error sending Telegram report:', error);
  }
}

/**
 * Optimize signal weights
 */
export async function optimizeSignalWeights(env: Env): Promise<void> {
  const now = Date.now();
  console.log(`[Weight Optimizer] Starting weekly optimization at ${new Date(now).toISOString()}`);
  
  try {
    // Get current weights
    const currentWeights = await getCurrentWeights(env.KV);
    console.log('[Weight Optimizer] Current weights:', currentWeights);
    
    // Analyze factor performance
    const factorPerformance = await analyzeFactorPerformance(env.DB);
    
    // Calculate optimal weights
    const newWeights = calculateOptimalWeights(currentWeights, factorPerformance);
    
    // Calculate expected accuracy improvement
    const avgAccuracy = factorPerformance.reduce((sum, p) => sum + p.accuracy, 0) / factorPerformance.length;
    const accuracyImprovement = Math.max(0, avgAccuracy - 50) / 10; // Estimate improvement
    
    // Store new weights
    const version = await storeWeights(
      env.KV,
      newWeights,
      factorPerformance.reduce((sum, p) => sum + p.signal_count, 0),
      accuracyImprovement
    );
    
    // Store weight history
    await storeWeightHistory(
      env.DB,
      version,
      newWeights,
      factorPerformance.reduce((sum, p) => sum + p.signal_count, 0),
      accuracyImprovement
    );
    
    // Generate and send report
    const report = formatOptimizationReport(
      currentWeights,
      newWeights,
      version,
      factorPerformance.reduce((sum, p) => sum + p.signal_count, 0),
      accuracyImprovement
    );
    
    await sendOptimizationReport(env, report);
    
    console.log('[Weight Optimizer] Weight optimization completed successfully');
    
    // Log monitoring metrics
    await env.DB
      .prepare(`
        INSERT INTO system_monitoring (metric_name, metric_value, metadata, created_at)
        VALUES (?, ?, ?, ?)
      `)
      .bind(
        'weight_optimizer_run',
        version,
        JSON.stringify({
          new_weights: newWeights,
          factors_analyzed: factorPerformance.length
        }),
        now
      )
      .run();
    
  } catch (error) {
    console.error('[Weight Optimizer] Fatal error:', error);
    throw error;
  }
}

/**
 * Handle cron trigger
 */
export async function handleCron(env: Env): Promise<void> {
  await optimizeSignalWeights(env);
}
