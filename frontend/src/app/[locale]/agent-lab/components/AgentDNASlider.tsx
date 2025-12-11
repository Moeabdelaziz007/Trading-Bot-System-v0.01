'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface AgentDNASliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  lowLabel: string;
  highLabel: string;
  color: string;
  icon?: React.ReactNode;
}

export const AgentDNASlider: React.FC<AgentDNASliderProps> = ({
  label,
  value,
  onChange,
  min = 0,
  max = 100,
  lowLabel,
  highLabel,
  color,
  icon
}) => {
  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className="space-y-3">
      {/* Label & Value */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {icon && <span className={color}>{icon}</span>}
          <label className="text-sm font-mono font-bold text-white">
            {label}
          </label>
        </div>
        <span
          data-testid={`slider-value-${label.toLowerCase().replace(/\s+/g, '-')}`}
          className={`text-lg font-mono font-bold ${color} min-w-[3ch] text-right`}
        >
          {value}
        </span>
      </div>

      {/* Slider */}
      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-2 bg-axiom-bg rounded-lg appearance-none cursor-pointer slider-thumb"
          style={{
            background: `linear-gradient(to right, ${color.replace('text-', '')} 0%, ${color.replace('text-', '')} ${percentage}%, rgba(255,255,255,0.1) ${percentage}%, rgba(255,255,255,0.1) 100%)`
          }}
        />

        {/* DNA Strand Animation */}
        <motion.div
          className="absolute -top-1 h-4 w-4 rounded-full border-2"
          style={{
            left: `calc(${percentage}% - 8px)`,
            borderColor: color.replace('text-', ''),
            backgroundColor: 'rgba(0,0,0,0.8)'
          }}
          animate={{
            boxShadow: [
              `0 0 0px ${color.replace('text-', '')}`,
              `0 0 20px ${color.replace('text-', '')}`,
              `0 0 0px ${color.replace('text-', '')}`
            ]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>

      {/* Low/High Labels */}
      <div className="flex justify-between text-xs font-mono text-text-muted">
        <span>{lowLabel}</span>
        <span>{highLabel}</span>
      </div>

      <style jsx>{`
        .slider-thumb::-webkit-slider-thumb {
          appearance: none;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: ${color.replace('text-', '')};
          cursor: pointer;
          box-shadow: 0 0 10px ${color.replace('text-', '')};
        }
        
        .slider-thumb::-moz-range-thumb {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: ${color.replace('text-', '')};
          cursor: pointer;
          border: none;
          box-shadow: 0 0 10px ${color.replace('text-', '')};
        }
      `}</style>
    </div>
  );
};