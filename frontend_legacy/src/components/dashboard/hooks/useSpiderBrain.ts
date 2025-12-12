'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://trading-brain-v1.amrikyy1.workers.dev';

export interface Agent {
  id: string;
  name: string;
  icon: string;
  color: string;
  purpose: string;
  model: string;
  status: 'online' | 'offline' | 'degraded';
  latency: number;
}

export interface SpiderBrainStatus {
  agents: Agent[];
  totalOnline: number;
  averageLatency: number;
  lastUpdate: string;
}

export const useSpiderBrain = () => {
  const [status, setStatus] = useState<SpiderBrainStatus>({
    agents: [
      {
        id: 'core-hub',
        name: 'Core Hub',
        icon: 'Brain',
        color: 'cyan',
        purpose: 'Orchestration & Routing',
        model: 'Cloudflare Worker',
        status: 'online',
        latency: 12
      },
      {
        id: 'reflex',
        name: 'Reflex',
        icon: 'Zap',
        color: 'yellow',
        purpose: 'Fast Pattern Matching',
        model: 'Workers AI',
        status: 'online',
        latency: 8
      },
      {
        id: 'analyst',
        name: 'Analyst',
        icon: 'Microscope',
        color: 'purple',
        purpose: 'Deep Reasoning',
        model: 'GLM-4.5/Gemini',
        status: 'online',
        latency: 45
      },
      {
        id: 'guardian',
        name: 'Guardian',
        icon: 'Shield',
        color: 'red',
        purpose: 'Risk Validation',
        model: 'Workers AI',
        status: 'online',
        latency: 15
      },
      {
        id: 'collector',
        name: 'Collector',
        icon: 'Radio',
        color: 'green',
        purpose: 'Market Data',
        model: 'Finnhub/Finage',
        status: 'online',
        latency: 22
      },
      {
        id: 'journalist',
        name: 'Journalist',
        icon: 'Newspaper',
        color: 'blue',
        purpose: 'Daily Briefings',
        model: 'Gemini Flash',
        status: 'online',
        latency: 38
      },
      {
        id: 'strategist',
        name: 'Strategist',
        icon: 'Briefcase',
        color: 'gold',
        purpose: 'Portfolio Rebalancing',
        model: 'GLM-4.5',
        status: 'online',
        latency: 52
      }
    ],
    totalOnline: 7,
    averageLatency: 27,
    lastUpdate: new Date().toISOString()
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true);
        // Switch to unified dashboard endpoint for KV data
        const response = await axios.get(`${API_BASE}/api/dashboard`);

        // Check for 'spider_agents' from KV (unpacked in api.py) 
        // OR fallback to 'agents' if the API structure varies
        const agentsData = response.data.spider_agents || response.data.agents;

        if (agentsData) {
          // If it comes as string from KV, parse it
          const parsedAgents = typeof agentsData === 'string' ? JSON.parse(agentsData) : agentsData;

          setStatus(prev => ({
            ...prev,
            agents: parsedAgents.map((agent: any) => ({
              ...agent,
              // Ensure we keep static metadata if backend only sends status/latency
              ...prev.agents.find(a => a.id === agent.id)
            })),
            totalOnline: parsedAgents.filter((a: Agent) => a.status === 'online').length,
            averageLatency: response.data.averageLatency || prev.averageLatency,
            lastUpdate: new Date().toISOString()
          }));
        }
      } catch (error) {
        console.error('Failed to fetch spider brain status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // 5s updates for Agents

    return () => clearInterval(interval);
  }, []);

  return { status, loading };
};