/**
 * Dialectic and UI Constants
 * Used by Self-Play Learning Loop components
 */

// Color palette for dialectic visualization
export const COLORS = {
    core: '#3B82F6',      // Blue - Core agent
    shadow: '#EF4444',    // Red - Shadow agent
    synthesis: '#10B981', // Green - Synthesis
    neutral: '#6B7280',   // Gray - Neutral
    accent: '#00FFFF',    // Cyan - Accent
};

// Core Agent Monologue phrases for the War Room
export const CORE_MONOLOGUE = [
    "Analyzing market conditions...",
    "Evaluating risk parameters...",
    "Processing technical indicators...",
    "Synthesizing signal patterns...",
    "Computing optimal position size...",
    "Validating entry conditions...",
    "Cross-referencing historical data...",
];

// Shadow Agent Monologue phrases (adversarial perspective)
export const SHADOW_MONOLOGUE = [
    "Challenging core hypothesis...",
    "Stress-testing risk assumptions...",
    "Simulating adverse scenarios...",
    "Questioning signal confidence...",
    "Exploring alternative positions...",
    "Probing for hidden weaknesses...",
    "Maximizing regret analysis...",
];

// Mock fitness data for evolutionary optimization visualization
export const MOCK_FITNESS_DATA = [
    { generation: 1, fitness: 0.45, population: 100 },
    { generation: 5, fitness: 0.52, population: 120 },
    { generation: 10, fitness: 0.61, population: 128 },
    { generation: 15, fitness: 0.68, population: 128 },
    { generation: 20, fitness: 0.74, population: 128 },
    { generation: 25, fitness: 0.82, population: 128 },
    { generation: 30, fitness: 0.89, population: 128 },
    { generation: 35, fitness: 0.93, population: 128 },
    { generation: 40, fitness: 0.95, population: 128 },
];

// Mock circuit breaker data for resilience monitoring
export const MOCK_CIRCUIT_BREAKERS = [
    { id: 'broker-api', name: 'Broker API', status: 'CLOSED', failures: 0, lastTrip: null, latency: '12ms', lastReset: '2h ago', totalCycles: 1248, avgLatency: '14ms' },
    { id: 'price-feed', name: 'Price Feed', status: 'CLOSED', failures: 0, lastTrip: null, latency: '8ms', lastReset: '1h ago', totalCycles: 8924, avgLatency: '9ms' },
    { id: 'ai-engine', name: 'AI Engine', status: 'CLOSED', failures: 1, lastTrip: null, latency: '45ms', lastReset: '30m ago', totalCycles: 542, avgLatency: '52ms' },
    { id: 'database', name: 'Database', status: 'CLOSED', failures: 0, lastTrip: null, latency: '3ms', lastReset: '4h ago', totalCycles: 15842, avgLatency: '4ms' },
    { id: 'telegram-bot', name: 'Telegram Bot', status: 'CLOSED', failures: 0, lastTrip: null, latency: '28ms', lastReset: '6h ago', totalCycles: 3421, avgLatency: '31ms' },
];

export default { COLORS, CORE_MONOLOGUE, SHADOW_MONOLOGUE, MOCK_FITNESS_DATA, MOCK_CIRCUIT_BREAKERS };
