'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, User, Shield, Zap, Brain, Building2 } from 'lucide-react';
import { AgentDNASlider } from './AgentDNASlider';
import { Input, Textarea, Field, Label } from '@headlessui/react';

interface AgentConfig {
  name: string;
  description: string;
  avatar: string | null;
  dna: {
    riskTolerance: number;
    tradeFrequency: number;
    intelligenceLevel: number;
  };
  broker: 'capital' | 'alpaca' | 'bybit';
}

interface AgentBuilderProps {
  config: AgentConfig;
  onChange: (config: AgentConfig) => void;
}

export const AgentBuilder: React.FC<AgentBuilderProps> = ({ config, onChange }) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (event) => {
        onChange({ ...config, avatar: event.target?.result as string });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        onChange({ ...config, avatar: event.target?.result as string });
      };
      reader.readAsDataURL(file);
    }
  };

  const brokers = [
    { id: 'capital', name: 'Capital.com', color: 'text-axiom-neon-blue' },
    { id: 'alpaca', name: 'Alpaca', color: 'text-axiom-neon-green' },
    { id: 'bybit', name: 'Bybit', color: 'text-axiom-neon-purple' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 pb-4 border-b border-glass-border">
        <User className="w-6 h-6 text-axiom-neon-cyan" />
        <h2 className="text-xl font-mono font-bold text-white tracking-tight">
          AGENT_IDENTITY
        </h2>
      </div>

      {/* Avatar Upload - Hexagon */}
      <div className="flex flex-col items-center">
        <div
          onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          className={`relative w-32 h-32 transition-all ${dragActive ? 'scale-105' : ''}`}
        >
          {/* Hexagon Shape */}
          <div className={`w-full h-full relative overflow-hidden ${
            config.avatar 
              ? 'border-2 border-axiom-neon-cyan shadow-glow-cyan' 
              : 'border-2 border-dashed border-glass-border hover:border-axiom-neon-cyan'
          }`}
            style={{
              clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)'
            }}
          >
            {config.avatar ? (
              <img 
                src={config.avatar} 
                alt="Agent Avatar" 
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full bg-axiom-surface flex items-center justify-center">
                <Upload className="w-8 h-8 text-text-muted" />
              </div>
            )}
          </div>

          {/* File Input */}
          <input
            type="file"
            accept="image/*"
            onChange={handleFileInput}
            className="absolute inset-0 opacity-0 cursor-pointer"
          />
        </div>
        <p className="text-xs text-text-muted font-mono mt-2">
          UPLOAD_AVATAR
        </p>
      </div>

      {/* Name Input */}
      <Field>
        <Label className="block text-sm font-mono text-text-muted mb-2">
          AGENT_NAME
        </Label>
        <Input
          value={config.name}
          onChange={(e) => onChange({ ...config, name: e.target.value })}
          placeholder="e.g., Alpha Predator"
          className="w-full bg-axiom-bg border border-glass-border rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-axiom-neon-cyan transition-colors data-[focus]:border-axiom-neon-cyan"
        />
      </Field>

      {/* Description */}
      <Field>
        <Label className="block text-sm font-mono text-text-muted mb-2">
          STRATEGY_DESCRIPTION
        </Label>
        <Textarea
          value={config.description}
          onChange={(e) => onChange({ ...config, description: e.target.value })}
          placeholder="Describe your agent's trading philosophy..."
          rows={3}
          className="w-full bg-axiom-bg border border-glass-border rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-axiom-neon-cyan transition-colors resize-none data-[focus]:border-axiom-neon-cyan"
        />
      </Field>

      {/* DNA Sliders */}
      <div className="space-y-6 pt-4 border-t border-glass-border">
        <h3 className="text-sm font-mono font-bold text-white flex items-center gap-2">
          <Shield className="w-4 h-4 text-axiom-neon-purple" />
          DNA_CONFIGURATION
        </h3>

        <AgentDNASlider
          label="RISK_TOLERANCE"
          value={config.dna.riskTolerance}
          onChange={(value) => onChange({ 
            ...config, 
            dna: { ...config.dna, riskTolerance: value }
          })}
          lowLabel="Conservative"
          highLabel="Aggressive"
          color="text-axiom-neon-red"
          icon={<Shield className="w-4 h-4" />}
        />

        <AgentDNASlider
          label="TRADE_FREQUENCY"
          value={config.dna.tradeFrequency}
          onChange={(value) => onChange({ 
            ...config, 
            dna: { ...config.dna, tradeFrequency: value }
          })}
          lowLabel="Swing Trader"
          highLabel="Scalper"
          color="text-axiom-neon-gold"
          icon={<Zap className="w-4 h-4" />}
        />

        <AgentDNASlider
          label="INTELLIGENCE_LEVEL"
          value={config.dna.intelligenceLevel}
          onChange={(value) => onChange({ 
            ...config, 
            dna: { ...config.dna, intelligenceLevel: value }
          })}
          lowLabel="Basic Rules"
          highLabel="GLM-4.5 AI"
          color="text-axiom-neon-purple"
          icon={<Brain className="w-4 h-4" />}
        />
      </div>

      {/* Broker Selection */}
      <div className="space-y-3 pt-4 border-t border-glass-border">
        <h3 className="text-sm font-mono font-bold text-white flex items-center gap-2">
          <Building2 className="w-4 h-4 text-axiom-neon-blue" />
          BROKER_SELECTION
        </h3>

        <div className="grid grid-cols-3 gap-2">
          {brokers.map((broker) => (
            <motion.button
              key={broker.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onChange({ ...config, broker: broker.id as any })}
              className={`p-3 rounded-lg border-2 transition-all ${
                config.broker === broker.id
                  ? `border-axiom-neon-cyan bg-axiom-neon-cyan/10 shadow-glow-cyan`
                  : 'border-glass-border bg-axiom-bg hover:border-glass-border/50'
              }`}
            >
              <p className={`text-xs font-mono font-bold ${
                config.broker === broker.id ? 'text-axiom-neon-cyan' : 'text-text-muted'
              }`}>
                {broker.name}
              </p>
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );
};