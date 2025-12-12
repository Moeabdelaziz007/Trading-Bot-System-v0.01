"use client";
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    Bot,
    Brain,
    Shield,
    Radar,
    Database,
    Newspaper,
    Play,
    Pause,
    RefreshCw,
    Activity,
    Zap,
    TrendingUp
} from 'lucide-react';

// Spider Agent Types
interface SpiderAgent {
    id: string;
    name: string;
    nameAr: string;
    description: string;
    descriptionAr: string;
    icon: React.ElementType;
    status: 'active' | 'idle' | 'error';
    lastRun: string;
    totalRuns: number;
    successRate: number;
    model: string;
    cost: string;
    color: string;
}

// Spider Agents Configuration
const SPIDER_AGENTS: SpiderAgent[] = [
    {
        id: 'core-hub',
        name: 'Core Hub',
        nameAr: 'المركز الرئيسي',
        description: 'Dispatcher & Orchestrator - Controls all spiders',
        descriptionAr: 'الموزع والمنظم - يتحكم في جميع العناكب',
        icon: Brain,
        status: 'active',
        lastRun: '1 min ago',
        totalRuns: 1440,
        successRate: 99.8,
        model: 'Cloudflare Worker',
        cost: 'FREE',
        color: 'var(--neon-cyan)'
    },
    {
        id: 'reflex',
        name: 'Reflex Spider',
        nameAr: 'عنكبوت الانعكاس',
        description: 'Fast pattern matching every 5 minutes',
        descriptionAr: 'مطابقة الأنماط السريعة كل 5 دقائق',
        icon: Zap,
        status: 'active',
        lastRun: '3 min ago',
        totalRuns: 288,
        successRate: 97.2,
        model: 'Workers AI (Llama 3.1)',
        cost: 'FREE',
        color: 'var(--neon-green)'
    },
    {
        id: 'analyst',
        name: 'Analyst Spider',
        nameAr: 'عنكبوت المحلل',
        description: 'Deep reasoning & strategy every hour',
        descriptionAr: 'التفكير العميق والاستراتيجية كل ساعة',
        icon: TrendingUp,
        status: 'active',
        lastRun: '45 min ago',
        totalRuns: 24,
        successRate: 100,
        model: 'GLM-4.5 Vision',
        cost: '$0.02/day',
        color: 'var(--neon-purple)'
    },
    {
        id: 'guardian',
        name: 'Guardian Spider',
        nameAr: 'عنكبوت الحارس',
        description: 'Risk validation before every trade',
        descriptionAr: 'التحقق من المخاطر قبل كل صفقة',
        icon: Shield,
        status: 'active',
        lastRun: '2 min ago',
        totalRuns: 156,
        successRate: 100,
        model: 'Workers AI (Risk Mode)',
        cost: 'FREE',
        color: 'var(--neon-magenta)'
    },
    {
        id: 'collector',
        name: 'Collector Spider',
        nameAr: 'عنكبوت الجامع',
        description: 'Data aggregation from markets & news',
        descriptionAr: 'جمع البيانات من الأسواق والأخبار',
        icon: Database,
        status: 'active',
        lastRun: '30 sec ago',
        totalRuns: 1440,
        successRate: 98.5,
        model: 'Finnhub + Capital.com',
        cost: 'FREE',
        color: 'var(--neon-blue)'
    },
    {
        id: 'journalist',
        name: 'Journalist Spider',
        nameAr: 'عنكبوت الصحفي',
        description: 'Daily market briefings & reports',
        descriptionAr: 'التقارير اليومية وموجزات السوق',
        icon: Newspaper,
        status: 'idle',
        lastRun: '6 hours ago',
        totalRuns: 7,
        successRate: 100,
        model: 'Gemini Flash',
        cost: 'FREE',
        color: 'var(--neon-yellow)'
    }
];

export default function BotsPage() {
    const [agents, setAgents] = useState(SPIDER_AGENTS);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [systemStatus, setSystemStatus] = useState<'online' | 'paused' | 'error'>('online');

    // Fetch real status from backend
    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const res = await fetch('/api/status');
                if (res.ok) {
                    // API connected successfully
                    setSystemStatus('online');
                }
            } catch {
                setSystemStatus('error');
            }
        };
        fetchStatus();
        const interval = setInterval(fetchStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        // Simulate refresh
        await new Promise(r => setTimeout(r, 1000));
        setIsRefreshing(false);
    };

    const toggleAgent = (id: string) => {
        setAgents(prev => prev.map(agent =>
            agent.id === id
                ? { ...agent, status: agent.status === 'active' ? 'idle' : 'active' }
                : agent
        ));
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'text-[var(--neon-green)]';
            case 'idle': return 'text-[var(--text-dim)]';
            case 'error': return 'text-red-500';
            default: return 'text-[var(--text-dim)]';
        }
    };

    const getStatusBg = (status: string) => {
        switch (status) {
            case 'active': return 'bg-[var(--neon-green)]/20';
            case 'idle': return 'bg-[var(--text-dim)]/20';
            case 'error': return 'bg-red-500/20';
            default: return 'bg-[var(--text-dim)]/20';
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Page Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                        <Bot className="w-7 h-7 text-[var(--neon-purple)]" />
                        Spider Web AI Agents
                    </h1>
                    <p className="text-sm text-[var(--text-muted)] mt-1">
                        شبكة العناكب الذكية - 6 وكلاء يعملون بتناغم
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    {/* System Status */}
                    <div className={`px-4 py-2 rounded-xl ${getStatusBg(systemStatus)} flex items-center gap-2`}>
                        <span className={`w-2 h-2 rounded-full ${systemStatus === 'online' ? 'bg-[var(--neon-green)] animate-pulse' : 'bg-red-500'}`} />
                        <span className={`text-sm font-medium ${getStatusColor(systemStatus)}`}>
                            {systemStatus === 'online' ? 'System Online' : 'System Error'}
                        </span>
                    </div>

                    {/* Refresh Button */}
                    <button
                        onClick={handleRefresh}
                        className="p-2.5 rounded-xl bg-[var(--surface)] border border-[var(--glass-border)] hover:border-[var(--neon-cyan)] transition-colors"
                    >
                        <RefreshCw className={`w-5 h-5 text-white ${isRefreshing ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* Stats Banner */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: 'Active Agents', value: agents.filter(a => a.status === 'active').length, icon: Activity, color: 'var(--neon-green)' },
                    { label: 'Total Runs (24h)', value: agents.reduce((sum, a) => sum + a.totalRuns, 0).toLocaleString(), icon: Radar, color: 'var(--neon-cyan)' },
                    { label: 'Avg Success Rate', value: `${(agents.reduce((sum, a) => sum + a.successRate, 0) / agents.length).toFixed(1)}%`, icon: TrendingUp, color: 'var(--neon-purple)' },
                    { label: 'Daily Cost', value: '$0.02', icon: Zap, color: 'var(--neon-yellow)' }
                ].map((stat, idx) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="bento-card p-4"
                    >
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg" style={{ backgroundColor: `${stat.color}20` }}>
                                <stat.icon className="w-5 h-5" style={{ color: stat.color }} />
                            </div>
                            <div>
                                <p className="text-xs text-[var(--text-dim)] uppercase">{stat.label}</p>
                                <p className="text-xl font-bold font-mono text-white">{stat.value}</p>
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Spider Agents Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {agents.map((agent, idx) => (
                    <motion.div
                        key={agent.id}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: idx * 0.1 }}
                        className="bento-card p-5 hover:border-[var(--neon-purple)]/50 transition-colors"
                    >
                        {/* Agent Header */}
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div
                                    className="w-12 h-12 rounded-xl flex items-center justify-center"
                                    style={{ backgroundColor: `${agent.color}20` }}
                                >
                                    <agent.icon className="w-6 h-6" style={{ color: agent.color }} />
                                </div>
                                <div>
                                    <h3 className="text-base font-bold text-white">{agent.name}</h3>
                                    <p className="text-xs text-[var(--text-dim)]">{agent.nameAr}</p>
                                </div>
                            </div>

                            {/* Status Badge */}
                            <div className={`px-2.5 py-1 rounded-full text-xs font-medium ${getStatusBg(agent.status)} ${getStatusColor(agent.status)}`}>
                                {agent.status === 'active' ? '● Active' : agent.status === 'idle' ? '○ Idle' : '✕ Error'}
                            </div>
                        </div>

                        {/* Description */}
                        <p className="text-sm text-[var(--text-muted)] mb-4">
                            {agent.description}
                        </p>

                        {/* Stats Grid */}
                        <div className="grid grid-cols-2 gap-3 mb-4">
                            <div className="bg-[var(--void)] rounded-lg p-2.5">
                                <p className="text-[10px] text-[var(--text-dim)] uppercase">Last Run</p>
                                <p className="text-sm font-mono text-white">{agent.lastRun}</p>
                            </div>
                            <div className="bg-[var(--void)] rounded-lg p-2.5">
                                <p className="text-[10px] text-[var(--text-dim)] uppercase">Success Rate</p>
                                <p className="text-sm font-mono text-[var(--neon-green)]">{agent.successRate}%</p>
                            </div>
                            <div className="bg-[var(--void)] rounded-lg p-2.5">
                                <p className="text-[10px] text-[var(--text-dim)] uppercase">Model</p>
                                <p className="text-xs font-mono text-white truncate">{agent.model}</p>
                            </div>
                            <div className="bg-[var(--void)] rounded-lg p-2.5">
                                <p className="text-[10px] text-[var(--text-dim)] uppercase">Cost</p>
                                <p className="text-sm font-mono" style={{ color: agent.cost === 'FREE' ? 'var(--neon-green)' : 'var(--neon-yellow)' }}>
                                    {agent.cost}
                                </p>
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-2">
                            <button
                                onClick={() => toggleAgent(agent.id)}
                                className={`flex-1 py-2.5 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-colors ${agent.status === 'active'
                                    ? 'bg-[var(--neon-green)]/20 text-[var(--neon-green)] hover:bg-[var(--neon-green)]/30'
                                    : 'bg-[var(--surface)] text-white hover:bg-white/10'
                                    }`}
                            >
                                {agent.status === 'active' ? (
                                    <>
                                        <Pause className="w-4 h-4" />
                                        Pause
                                    </>
                                ) : (
                                    <>
                                        <Play className="w-4 h-4" />
                                        Activate
                                    </>
                                )}
                            </button>
                            <button className="p-2.5 rounded-xl bg-[var(--surface)] text-white hover:bg-white/10 transition-colors">
                                <RefreshCw className="w-4 h-4" />
                            </button>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Web Architecture Visualization */}
            <div className="bento-card p-6">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    🕸️ Spider Web Architecture
                </h2>
                <div className="text-center text-[var(--text-muted)] py-8">
                    <pre className="text-xs font-mono inline-block text-left">
                        {`                    ┌─────────────┐
                    │  Core Hub   │
                    │  (Worker)   │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │   Reflex    │ │   Analyst   │ │  Guardian   │
    │  (Fast AI)  │ │  (Deep AI)  │ │  (Risk AI)  │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           └───────────────┴───────────────┘
                           │
                    ┌──────▼──────┐
                    │  Collector  │
                    │   (Data)    │
                    └─────────────┘`}
                    </pre>
                </div>
            </div>
        </div>
    );
}
