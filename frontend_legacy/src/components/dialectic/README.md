# Dialectic Components

This directory contains the UI components for the Axiom-Shadow dialectic system.

## Components

### AgentCard
Displays information about either the Core (Thesis) or Shadow (Antithesis) agent.

Props:
- `type`: 'core' | 'shadow'
- `title`: Display title for the agent
- `text`: Current streaming text from the agent
- `confidence`: Confidence percentage (for Core agent)
- `regret`: Regret percentage (for Shadow agent)

### DecisionOrb
Visualizes the synthesis decision between Core and Shadow agents.

Props:
- `decision`: The final decision string
- `status`: 'thinking' | 'decided'

### FitnessChart
Displays the evolutionary fitness landscape of the learning loop.

Props: None

## Hooks

### useDialecticStream
Custom hook that connects to the SSE endpoint and manages the dialectic data stream.

Returns:
- `coreText`: Current text from Core agent
- `shadowText`: Current text from Shadow agent
- `decision`: Final decision
- `isLoading`: Connection status
- `error`: Error state

## Pages

### Shadow Center (/dashboard/shadow-center)
Main War Room interface displaying the real-time dialectic process.

### Active Dialectic Status (Widget)
Compact widget for the main dashboard showing live dialectic status.