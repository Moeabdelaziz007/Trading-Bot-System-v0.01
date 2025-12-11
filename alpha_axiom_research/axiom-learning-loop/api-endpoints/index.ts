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

interface WeightHistory {
  version: number;
  weights: SignalWeights;
  total_signals_analyzed: number;
  accuracy_improvement: number;
  created_at: number;
}

interface APIResponse {
  success: boolean;
  data?: any;
  error?: string;
  timestamp: number;
}

/**
 * Get accuracy metrics per symbol and direction
 */
export async function getLearningMetrics(env: Env): Promise<APIResponse> {
  try {
    const query = `
      SELECT 
        symbol,
        signal_direction,
        timeframe,
        total_signals,
        correct_signals,
        avg_return,
        max_return,
        min_return,
        accuracy
      FROM learning_metrics
      WHERE metric_date = DATE('now')
      ORDER BY accuracy DESC
    `;
    
    const result = await env.DB.prepare(query).all<LearningMetric>();
    
    return {
      success: true,
      data: result.results,
      timestamp: Date.now()
    };
  } catch (error) {
    console.error('[API] Error fetching learning metrics:', error);
    return {
      success: false,
      error: 'Failed to fetch metrics',
      timestamp: Date.now()
    };
  }
}

/**
 * Get current signal weights
 */
export async function getSignalWeights(env: Env): Promise<APIResponse> {
  try {
    const weightsStr = await env.KV.get('signal_weights:latest');
    
    if (!weightsStr) {
      return {
        success: false,
        error: 'No weights found',
        timestamp: Date.now()
      };
    }
    
    const data = JSON.parse(weightsStr);
    
    return {
      success: true,
      data: {
        weights: data.weights,
        updated_at: data.updated_at,
        based_on_signals: data.based_on_signals,
        version: data.version
      },
      timestamp: Date.now()
    };
  } catch (error) {
    console.error('[API] Error fetching signal weights:', error);
    return {
      success: false,
      error: 'Failed to fetch weights',
      timestamp: Date.now()
    };
  }
}

/**
 * Get latest weight history
 */
export async function getWeightHistory(env: Env): Promise<APIResponse> {
  try {
    const query = `
      SELECT 
        version,
        weights,
        total_signals_analyzed,
        accuracy_improvement,
        created_at
      FROM weight_history
      ORDER BY version DESC
      LIMIT 10
    `;
    
    const result = await env.DB.prepare(query).all<WeightHistory>();
    
    const history = result.results.map(h => ({
      version: h.version,
      weights: JSON.parse(h.weights),
      total_signals_analyzed: h.total_signals_analyzed,
      accuracy_improvement: h.accuracy_improvement,
      created_at: h.created_at
    }));
    
    return {
      success: true,
      data: history,
      timestamp: Date.now()
    };
  } catch (error) {
    console.error('[API] Error fetching weight history:', error);
    return {
      success: false,
      error: 'Failed to fetch weight history',
      timestamp: Date.now()
    };
  }
}

/**
 * Get latest Telegram report
 */
export async function getLatestReport(env: Env): Promise<APIResponse> {
  try {
    const query = `
      SELECT 
        report_type,
        report_date,
        report_content,
        sent_at
      FROM telegram_reports
      ORDER BY sent_at DESC
      LIMIT 1
    `;
    
    const result = await env.DB.prepare(query).first();
    
    if (!result) {
      return {
        success: false,
        error: 'No reports found',
        timestamp: Date.now()
      };
    }
    
    return {
      success: true,
      data: {
        type: result.report_type,
        date: result.report_date,
        content: result.report_content,
        sent_at: result.sent_at
      },
      timestamp: Date.now()
    };
  } catch (error) {
    console.error('[API] Error fetching latest report:', error);
    return {
      success: false,
      error: 'Failed to fetch report',
      timestamp: Date.now()
    };
  }
}

/**
 * Get overall system statistics
 */
export async function getSystemStats(env: Env): Promise<APIResponse> {
  try {
    // Total signals
    const totalSignalsQuery = `SELECT COUNT(*) as count FROM signal_events`;
    const totalSignals = await env.DB.prepare(totalSignalsQuery).first();
    
    // Completed signals
    const completedSignalsQuery = `
      SELECT COUNT(*) as count FROM signal_events WHERE status = 'completed'
    `;
    const completedSignals = await env.DB.prepare(completedSignalsQuery).first();
    
    // Accuracy by timeframe
    const accuracyQuery = `
      SELECT 
        AVG(CASE WHEN so.was_correct_1h = 1 THEN 1.0 ELSE 0.0 END) * 100 as accuracy_1h,
        AVG(CASE WHEN so.was_correct_4h = 1 THEN 1.0 ELSE 0.0 END) * 100 as accuracy_4h,
        AVG(CASE WHEN so.was_correct_24h = 1 THEN 1.0 ELSE 0.0 END) * 100 as accuracy_24h
      FROM signal_outcomes so
    `;
    const accuracy = await env.DB.prepare(accuracyQuery).first();
    
    // Recent signals (last 24 hours)
    const recentSignalsQuery = `
      SELECT 
        COUNT(*) as count,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
      FROM signal_events
      WHERE timestamp > (strftime('%s', 'now') - 24*3600) * 1000
    `;
    const recentSignals = await env.DB.prepare(recentSignalsQuery).first();
    
    return {
      success: true,
      data: {
        total_signals: totalSignals.count,
        completed_signals: completedSignals.count,
        completion_rate: totalSignals.count > 0 
          ? ((completedSignals.count / totalSignals.count) * 100).toFixed(1)
          : '0.0',
        accuracy_1h: accuracy.accuracy_1h || 0,
        accuracy_4h: accuracy.accuracy_4h || 0,
        accuracy_24h: accuracy.accuracy_24h || 0,
        recent_signals: recentSignals.count,
        recent_completed: recentSignals.completed
      },
      timestamp: Date.now()
    };
  } catch (error) {
    console.error('[API] Error fetching system stats:', error);
    return {
      success: false,
      error: 'Failed to fetch system stats',
      timestamp: Date.now()
    };
  }
}

/**
 * Get top performing symbols
 */
export async function getTopPerformers(env: Env): Promise<APIResponse> {
  try {
    const query = `
      SELECT 
        se.symbol,
        se.signal_direction,
        AVG(CASE WHEN so.was_correct_1h = 1 THEN 1.0 ELSE 0.0 END) * 100 as accuracy,
        AVG(so.return_1h) as avg_return,
        COUNT(*) as signal_count
      FROM signal_events se
      JOIN signal_outcomes so ON se.id = so.signal_event_id
      WHERE so.was_correct_1h IS NOT NULL
      GROUP BY se.symbol, se.signal_direction
      HAVING COUNT(*) >= 10
      ORDER BY accuracy DESC
      LIMIT 10
    `;
    
    const result = await env.DB.prepare(query).all();
    
    return {
      success: true,
      data: result.results,
      timestamp: Date.now()
    };
  } catch (error) {
    console.error('[API] Error fetching top performers:', error);
    return {
      success: false,
      error: 'Failed to fetch top performers',
      timestamp: Date.now()
    };
  }
}

/**
 * Get worst performing symbols
 */
export async function getWorstPerformers(env: Env): Promise<APIResponse> {
  try {
    const query = `
      SELECT 
        se.symbol,
        se.signal_direction,
        AVG(CASE WHEN so.was_correct_1h = 1 THEN 1.0 ELSE 0.0 END) * 100 as accuracy,
        AVG(so.return_1h) as avg_return,
        COUNT(*) as signal_count
      FROM signal_events se
      JOIN signal_outcomes so ON se.id = so.signal_event_id
      WHERE so.was_correct_1h IS NOT NULL
      GROUP BY se.symbol, se.signal_direction
      HAVING COUNT(*) >= 10
      ORDER BY accuracy ASC
      LIMIT 10
    `;
    
    const result = await env.DB.prepare(query).all();
    
    return {
      success: true,
      data: result.results,
      timestamp: Date.now()
    };
  } catch (error) {
    console.error('[API] Error fetching worst performers:', error);
    return {
      success: false,
      error: 'Failed to fetch worst performers',
      timestamp: Date.now()
    };
  }
}

/**
 * Get monitoring metrics
 */
export async function getMonitoringMetrics(env: Env): Promise<APIResponse> {
  try {
    const query = `
      SELECT 
        metric_name,
        metric_value,
        metadata,
        created_at
      FROM system_monitoring
      WHERE created_at > (strftime('%s', 'now') - 7*24*3600) * 1000
      ORDER BY created_at DESC
      LIMIT 50
    `;
    
    const result = await env.DB.prepare(query).all();
    
    return {
      success: true,
      data: result.results,
      timestamp: Date.now()
    };
  } catch (error) {
    console.error('[API] Error fetching monitoring metrics:', error);
    return {
      success: false,
      error: 'Failed to fetch monitoring metrics',
      timestamp: Date.now()
    };
  }
}
