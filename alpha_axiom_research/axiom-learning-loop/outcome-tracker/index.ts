import { D1Database } from '@cloudflare/d1';
import { KVNamespace } from '@cloudflare/workers-types';

interface Env {
  DB: D1Database;
  KV: KVNamespace;
}

interface SignalEvent {
  id: number;
  signal_id: string;
  symbol: string;
  asset_type: string;
  signal_direction: string;
  price_at_signal: number;
  timestamp: number;
}

interface SignalOutcome {
  signal_event_id: number;
  price_1h_later?: number;
  return_1h?: number;
  was_correct_1h?: number;
  price_4h_later?: number;
  return_4h?: number;
  was_correct_4h?: number;
  price_24h_later?: number;
  return_24h?: number;
  was_correct_24h?: number;
  final_status: string;
  updated_at: number;
}

interface PriceData {
  symbol: string;
  price: number;
  timestamp: number;
}

/**
 * Fetch current price from appropriate API based on asset type
 */
async function fetchCurrentPrice(
  symbol: string,
  assetType: string,
  env: Env
): Promise<PriceData | null> {
  const now = Date.now();
  
  try {
    // Determine API based on asset type
    let price: number | null = null;
    
    if (assetType === 'crypto') {
      // Bybit API
      const response = await fetch(`https://api.bybit.com/v5/market/tickers?category=linear&symbol=${symbol}`);
      const data = await response.json();
      
      if (data.retCode === 0 && data.result.list.length > 0) {
        price = parseFloat(data.result.list[0].lastPrice);
      }
    } else if (assetType === 'stock' || assetType === 'forex') {
      // Finage API
      const apiKey = await env.KV.get('FINAGE_API_KEY');
      if (!apiKey) {
        console.error('FINAGE_API_KEY not found in KV');
        return null;
      }
      
      const response = await fetch(
        `https://api.finage.co.uk/last/stock?symbol=${symbol}&api_key=${apiKey}`
      );
      const data = await response.json();
      
      if (data.price) {
        price = data.price;
      }
    }
    
    if (price === null) {
      console.warn(`No price data found for ${symbol} (${assetType})`);
      return null;
    }
    
    return {
      symbol,
      price,
      timestamp: now
    };
  } catch (error) {
    console.error(`Error fetching price for ${symbol}:`, error);
    return null;
  }
}

/**
 * Calculate return percentage and correctness based on signal direction
 */
function calculateMetrics(
  signalDirection: string,
  priceAtSignal: number,
  currentPrice: number
): { returnPct: number; wasCorrect: boolean } {
  const returnPct = ((currentPrice - priceAtSignal) / priceAtSignal) * 100;
  
  let wasCorrect = false;
  
  // Adjust for direction
  if (['BUY', 'STRONG_BUY'].includes(signalDirection)) {
    wasCorrect = currentPrice > priceAtSignal;
  } else if (['SELL', 'STRONG_SELL'].includes(signalDirection)) {
    wasCorrect = currentPrice < priceAtSignal;
  } else if (signalDirection === 'NEUTRAL') {
    // Neutral signals are always correct (no action)
    wasCorrect = true;
  }
  
  return { returnPct, wasCorrect };
}

/**
 * Determine which timeframe to update based on signal age
 */
function determineTimeframe(signalTimestamp: number): '1h' | '4h' | '24h' {
  const now = Date.now();
  const ageMs = now - signalTimestamp;
  const ageHours = ageMs / (1000 * 60 * 60);
  
  if (ageHours >= 24) return '24h';
  if (ageHours >= 4) return '4h';
  return '1h';
}

/**
 * Update or insert signal outcome based on timeframe
 */
async function upsertSignalOutcome(
  db: D1Database,
  outcome: SignalOutcome
): Promise<void> {
  const { 
    signal_event_id,
    price_1h_later,
    return_1h,
    was_correct_1h,
    price_4h_later,
    return_4h,
    was_correct_4h,
    price_24h_later,
    return_24h,
    was_correct_24h,
    final_status,
    updated_at
  } = outcome;
  
  // Check if outcome exists
  const existing = await db
    .prepare('SELECT id FROM signal_outcomes WHERE signal_event_id = ?')
    .bind(signal_event_id)
    .first();
  
  if (existing) {
    // Update existing record
    await db
      .prepare(`
        UPDATE signal_outcomes SET
          price_1h_later = COALESCE(?, price_1h_later),
          return_1h = COALESCE(?, return_1h),
          was_correct_1h = COALESCE(?, was_correct_1h),
          price_4h_later = COALESCE(?, price_4h_later),
          return_4h = COALESCE(?, return_4h),
          was_correct_4h = COALESCE(?, was_correct_4h),
          price_24h_later = COALESCE(?, price_24h_later),
          return_24h = COALESCE(?, return_24h),
          was_correct_24h = COALESCE(?, was_correct_24h),
          final_status = ?,
          updated_at = ?
        WHERE signal_event_id = ?
      `)
      .bind(
        price_1h_later,
        return_1h,
        was_correct_1h,
        price_4h_later,
        return_4h,
        was_correct_4h,
        price_24h_later,
        return_24h,
        was_correct_24h,
        final_status,
        updated_at,
        signal_event_id
      )
      .run();
  } else {
    // Insert new record
    await db
      .prepare(`
        INSERT INTO signal_outcomes (
          signal_event_id, price_1h_later, return_1h, was_correct_1h,
          price_4h_later, return_4h, was_correct_4h,
          price_24h_later, return_24h, was_correct_24h,
          final_status, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `)
      .bind(
        signal_event_id,
        price_1h_later,
        return_1h,
        was_correct_1h,
        price_4h_later,
        return_4h,
        was_correct_4h,
        price_24h_later,
        return_24h,
        was_correct_24h,
        final_status,
        updated_at
      )
      .run();
  }
}

/**
 * Update signal event status to 'completed' when all timeframes are tracked
 */
async function updateSignalEventStatus(
  db: D1Database,
  signalId: number
): Promise<void> {
  await db
    .prepare('UPDATE signal_events SET status = ?, updated_at = ? WHERE id = ?')
    .bind('completed', Date.now(), signalId)
    .run();
}

/**
 * Track outcomes for pending signals (hourly cron job)
 */
export async function trackSignalOutcomes(env: Env): Promise<void> {
  const now = Date.now();
  const oneHourAgo = now - (1000 * 60 * 60);
  
  console.log(`[Outcome Tracker] Starting hourly tracking at ${new Date(now).toISOString()}`);
  
  try {
    // Fetch pending signals older than 1 hour
    const pendingSignals = await env.DB
      .prepare(`
        SELECT se.id, se.signal_id, se.symbol, se.asset_type, se.signal_direction,
               se.price_at_signal, se.timestamp
        FROM signal_events se
        LEFT JOIN signal_outcomes so ON se.id = so.signal_event_id
        WHERE so.id IS NULL
          AND se.timestamp < ?
          AND se.status = 'pending'
        LIMIT 50
      `)
      .bind(oneHourAgo)
      .all<SignalEvent>();
    
    if (pendingSignals.results.length === 0) {
      console.log('[Outcome Tracker] No pending signals to track');
      return;
    }
    
    console.log(`[Outcome Tracker] Found ${pendingSignals.results.length} pending signals`);
    
    let completedCount = 0;
    let errorCount = 0;
    
    // Process each signal
    for (const signal of pendingSignals.results) {
      try {
        const priceData = await fetchCurrentPrice(signal.symbol, signal.asset_type, env);
        
        if (!priceData) {
          console.warn(`[Outcome Tracker] Skipping ${signal.symbol} - no price data`);
          errorCount++;
          continue;
        }
        
        const { returnPct, wasCorrect } = calculateMetrics(
          signal.signal_direction,
          signal.price_at_signal,
          priceData.price
        );
        
        const timeframe = determineTimeframe(signal.timestamp);
        
        // Build outcome object based on timeframe
        const outcome: SignalOutcome = {
          signal_event_id: signal.id,
          final_status: 'incomplete',
          updated_at: now
        };
        
        if (timeframe === '1h') {
          outcome.price_1h_later = priceData.price;
          outcome.return_1h = returnPct;
          outcome.was_correct_1h = wasCorrect ? 1 : 0;
        } else if (timeframe === '4h') {
          outcome.price_4h_later = priceData.price;
          outcome.return_4h = returnPct;
          outcome.was_correct_4h = wasCorrect ? 1 : 0;
        } else if (timeframe === '24h') {
          outcome.price_24h_later = priceData.price;
          outcome.return_24h = returnPct;
          outcome.was_correct_24h = wasCorrect ? 1 : 0;
          outcome.final_status = 'complete';
        }
        
        // Upsert outcome
        await upsertSignalOutcome(env.DB, outcome);
        
        // Update signal status if complete
        if (outcome.final_status === 'complete') {
          await updateSignalEventStatus(env.DB, signal.id);
          completedCount++;
        }
        
        console.log(`[Outcome Tracker] Tracked ${signal.symbol} (${timeframe}): ${returnPct.toFixed(2)}%`);
      } catch (error) {
        console.error(`[Outcome Tracker] Error processing ${signal.symbol}:`, error);
        errorCount++;
      }
    }
    
    console.log(`[Outcome Tracker] Completed: ${completedCount}, Errors: ${errorCount}`);
    
    // Log monitoring metrics
    await env.DB
      .prepare(`
        INSERT INTO system_monitoring (metric_name, metric_value, metadata, created_at)
        VALUES (?, ?, ?, ?)
      `)
      .bind(
        'outcome_tracker_processed',
        pendingSignals.results.length,
        JSON.stringify({ completed: completedCount, errors: errorCount }),
        now
      )
      .run();
    
  } catch (error) {
    console.error('[Outcome Tracker] Fatal error:', error);
    throw error;
  }
}

/**
 * Handle cron trigger
 */
export async function handleCron(env: Env): Promise<void> {
  await trackSignalOutcomes(env);
}
