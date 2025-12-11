import { D1Database } from '@cloudflare/d1';
import { KVNamespace } from '@cloudflare/workers-types';

interface Env {
  DB: D1Database;
  KV: KVNamespace;
}

interface LearningMetric {
  symbol: string;
  signal_direction: string;
  timeframe: string;
  total_signals: number;
  correct_signals: number;
  avg_return: number;
  max_return: number;
  min_return: number;
  accuracy: number;
}

interface DailyReport {
  report_date: string;
  overall_accuracy_1h: number;
  overall_accuracy_4h: number;
  overall_accuracy_24h: number;
  total_signals_1h: number;
  total_signals_4h: number;
  total_signals_24h: number;
  best_performing_symbols: Array<{
    symbol: string;
    direction: string;
    accuracy: number;
    avg_return: number;
  }>;
  worst_performing_symbols: Array<{
    symbol: string;
    direction: string;
    accuracy: number;
    avg_return: number;
  }>;
  recommendation: string;
}

/**
 * Calculate daily learning metrics
 */
async function calculateDailyMetrics(db: D1Database): Promise<Array<LearningMetric>> {
  const now = new Date();
  const today = now.toISOString().split('T')[0];
  
  console.log(`[Metrics Aggregator] Calculating daily metrics for ${today}`);
  
  const metrics: Array<LearningMetric> = [];
  
  // Calculate metrics for each timeframe
  for (const timeframe of ['1h', '4h', '24h']) {
    const query = `
      SELECT 
        se.symbol,
        se.signal_direction,
        '${timeframe}' as timeframe,
        COUNT(*) as total_signals,
        SUM(CASE WHEN so.was_correct_${timeframe} = 1 THEN 1 ELSE 0 END) as correct_signals,
        ROUND(AVG(so.return_${timeframe}), 4) as avg_return,
        MAX(so.return_${timeframe}) as max_return,
        MIN(so.return_${timeframe}) as min_return,
        ROUND(
          (SUM(CASE WHEN so.was_correct_${timeframe} = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(*),
          2
        ) as accuracy
      FROM signal_events se
      JOIN signal_outcomes so ON se.id = so.signal_event_id
      WHERE so.was_correct_${timeframe} IS NOT NULL
        AND DATE(se.timestamp / 1000, 'unixepoch') = DATE('now')
      GROUP BY se.symbol, se.signal_direction
    `;
    
    const result = await db.prepare(query).all<LearningMetric>();
    metrics.push(...result.results);
  }
  
  console.log(`[Metrics Aggregator] Calculated ${metrics.length} metrics`);
  
  return metrics;
}

/**
 * Store metrics in D1 database
 */
async function storeMetrics(
  db: D1Database,
  metrics: Array<LearningMetric>
): Promise<void> {
  const now = Date.now();
  const today = new Date().toISOString().split('T')[0];
  
  console.log(`[Metrics Aggregator] Storing ${metrics.length} metrics`);
  
  // Delete existing metrics for today
  await db
    .prepare('DELETE FROM learning_metrics WHERE metric_date = ?')
    .bind(today)
    .run();
  
  // Insert new metrics
  const insertStmt = db.prepare(`
    INSERT INTO learning_metrics (
      metric_date, symbol, signal_direction, timeframe,
      total_signals, correct_signals, avg_return, max_return, min_return, accuracy,
      created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  for (const metric of metrics) {
    await insertStmt
      .bind(
        today,
        metric.symbol,
        metric.signal_direction,
        metric.timeframe,
        metric.total_signals,
        metric.correct_signals,
        metric.avg_return,
        metric.max_return,
        metric.min_return,
        metric.accuracy,
        now,
        now
      )
      .run();
  }
  
  console.log('[Metrics Aggregator] Metrics stored successfully');
}

/**
 * Generate comprehensive daily report
 */
async function generateDailyReport(db: D1Database): Promise<DailyReport> {
  const now = new Date();
  const today = now.toISOString().split('T')[0];
  
  // Calculate overall accuracy
  const overallQuery = `
    SELECT 
      AVG(CASE WHEN so.was_correct_1h = 1 THEN 1.0 ELSE 0.0 END) * 100 as overall_accuracy_1h,
      COUNT(CASE WHEN so.was_correct_1h IS NOT NULL THEN 1 END) as total_signals_1h,
      AVG(CASE WHEN so.was_correct_4h = 1 THEN 1.0 ELSE 0.0 END) * 100 as overall_accuracy_4h,
      COUNT(CASE WHEN so.was_correct_4h IS NOT NULL THEN 1 END) as total_signals_4h,
      AVG(CASE WHEN so.was_correct_24h = 1 THEN 1.0 ELSE 0.0 END) * 100 as overall_accuracy_24h,
      COUNT(CASE WHEN so.was_correct_24h IS NOT NULL THEN 1 END) as total_signals_24h
    FROM signal_events se
    JOIN signal_outcomes so ON se.id = so.signal_event_id
    WHERE DATE(se.timestamp / 1000, 'unixepoch') = DATE('now')
  `;
  
  const overallResult = await db.prepare(overallQuery).first();
  
  // Find best and worst performers
  const performanceQuery = `
    SELECT 
      se.symbol,
      se.signal_direction,
      AVG(CASE WHEN so.was_correct_1h = 1 THEN 1.0 ELSE 0.0 END) * 100 as accuracy,
      AVG(so.return_1h) as avg_return
    FROM signal_events se
    JOIN signal_outcomes so ON se.id = so.signal_event_id
    WHERE so.was_correct_1h IS NOT NULL
      AND DATE(se.timestamp / 1000, 'unixepoch') = DATE('now')
    GROUP BY se.symbol, se.signal_direction
    HAVING COUNT(*) >= 5  -- Minimum 5 signals
    ORDER BY accuracy DESC
  `;
  
  const performanceResult = await db.prepare(performanceQuery).all();
  
  const bestPerformers = performanceResult.results.slice(0, 5);
  const worstPerformers = performanceResult.results.slice(-5).reverse();
  
  // Generate recommendation
  const recommendation = generateRecommendation(
    overallResult.overall_accuracy_1h,
    bestPerformers,
    worstPerformers
  );
  
  const report: DailyReport = {
    report_date: today,
    overall_accuracy_1h: overallResult.overall_accuracy_1h || 0,
    overall_accuracy_4h: overallResult.overall_accuracy_4h || 0,
    overall_accuracy_24h: overallResult.overall_accuracy_24h || 0,
    total_signals_1h: overallResult.total_signals_1h || 0,
    total_signals_4h: overallResult.total_signals_4h || 0,
    total_signals_24h: overallResult.total_signals_24h || 0,
    best_performing_symbols: bestPerformers.map(p => ({
      symbol: p.symbol,
      direction: p.signal_direction,
      accuracy: p.accuracy,
      avg_return: p.avg_return
    })),
    worst_performing_symbols: worstPerformers.map(p => ({
      symbol: p.symbol,
      direction: p.signal_direction,
      accuracy: p.accuracy,
      avg_return: p.avg_return
    })),
    recommendation
  };
  
  return report;
}

/**
 * Generate recommendation based on performance
 */
function generateRecommendation(
  overallAccuracy: number,
  bestPerformers: any[],
  worstPerformers: any[]
): string {
  const recommendations: string[] = [];
  
  if (overallAccuracy > 65) {
    recommendations.push("Excellent performance! Maintain current strategy.");
  } else if (overallAccuracy < 50) {
    recommendations.push("Performance below target. Consider adjusting signal parameters.");
  }
  
  if (bestPerformers.length > 0) {
    const topSymbol = bestPerformers[0];
    recommendations.push(
      `Top performer: ${topSymbol.symbol} ${topSymbol.direction} (${topSymbol.accuracy.toFixed(1)}% accuracy)`
    );
  }
  
  if (worstPerformers.length > 0) {
    const worstSymbol = worstPerformers[0];
    recommendations.push(
      `Needs attention: ${worstSymbol.symbol} ${worstSymbol.direction} (${worstSymbol.accuracy.toFixed(1)}% accuracy)`
    );
  }
  
  return recommendations.join(' ');
}

/**
 * Format report for Telegram
 */
function formatTelegramReport(report: DailyReport): string {
  const emoji = {
    chart: '📊',
    target: '🎯',
    trophy: '🏆',
    warning: '⚠️',
    lightbulb: '💡',
    check: '✅',
    x: '❌'
  };
  
  return `${emoji.chart} Daily Learning Report

${emoji.target} Overall Accuracy:
• 1h: ${report.overall_accuracy_1h.toFixed(1)}% (${report.total_signals_1h} signals)
• 4h: ${report.overall_accuracy_4h.toFixed(1)}% (${report.total_signals_4h} signals)
• 24h: ${report.overall_accuracy_24h.toFixed(1)}% (${report.total_signals_24h} signals)

${emoji.trophy} Top Performers:
${report.best_performing_symbols.slice(0, 3).map(p => 
  `• ${p.symbol} ${p.direction}: ${p.accuracy.toFixed(1)}% (${p.avg_return.toFixed(2)}% avg return)`
).join('\n')}

${emoji.warning} Underperformers:
${report.worst_performing_symbols.slice(0, 3).map(p => 
  `• ${p.symbol} ${p.direction}: ${p.accuracy.toFixed(1)}% (${p.avg_return.toFixed(2)}% avg return)`
).join('\n')}

${emoji.lightbulb} ${report.recommendation}

${emoji.check} System is learning...`;
}

/**
 * Send report to Telegram
 */
async function sendTelegramReport(env: Env, report: string): Promise<void> {
  const telegramBotToken = await env.KV.get('TELEGRAM_BOT_TOKEN');
  const telegramChatId = await env.KV.get('TELEGRAM_CHAT_ID');
  
  if (!telegramBotToken || !telegramChatId) {
    console.warn('[Metrics Aggregator] Telegram credentials not configured');
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
      console.log('[Metrics Aggregator] Telegram report sent successfully');
      
      // Store in database
      const now = Date.now();
      await env.DB
        .prepare(`
          INSERT INTO telegram_reports (report_type, report_date, report_content, sent_at, created_at)
          VALUES (?, ?, ?, ?, ?)
        `)
        .bind('daily', report.report_date, report, now, now)
        .run();
    } else {
      console.error('[Metrics Aggregator] Failed to send Telegram report');
    }
  } catch (error) {
    console.error('[Metrics Aggregator] Error sending Telegram report:', error);
  }
}

/**
 * Aggregate daily metrics and generate report
 */
export async function aggregateLearningMetrics(env: Env): Promise<void> {
  const now = Date.now();
  console.log(`[Metrics Aggregator] Starting daily aggregation at ${new Date(now).toISOString()}`);
  
  try {
    // Calculate metrics
    const metrics = await calculateDailyMetrics(env.DB);
    
    // Store metrics
    await storeMetrics(env.DB, metrics);
    
    // Generate report
    const report = await generateDailyReport(env.DB);
    
    // Format for Telegram
    const telegramReport = formatTelegramReport(report);
    
    // Send to Telegram
    await sendTelegramReport(env, telegramReport);
    
    console.log('[Metrics Aggregator] Daily aggregation completed successfully');
    
    // Log monitoring metrics
    await env.DB
      .prepare(`
        INSERT INTO system_monitoring (metric_name, metric_value, metadata, created_at)
        VALUES (?, ?, ?, ?)
      `)
      .bind(
        'metrics_aggregator_run',
        metrics.length,
        JSON.stringify({
          overall_accuracy_1h: report.overall_accuracy_1h,
          overall_accuracy_4h: report.overall_accuracy_4h,
          overall_accuracy_24h: report.overall_accuracy_24h
        }),
        now
      )
      .run();
    
  } catch (error) {
    console.error('[Metrics Aggregator] Fatal error:', error);
    throw error;
  }
}

/**
 * Handle cron trigger
 */
export async function handleCron(env: Env): Promise<void> {
  await aggregateLearningMetrics(env);
}
