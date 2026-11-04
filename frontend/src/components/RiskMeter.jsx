import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function RiskMeter({ score = 0, riskLevel = 'LOW', reportCount = 0 }) {
  const normalizedScore = Math.min(Math.max(score, 0), 100);
  
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  const getColorConfig = () => {
    if (normalizedScore >= 70 || (riskLevel && riskLevel.toUpperCase() === 'HIGH')) {
      return {
        stroke: '#f43f5e',
        glow: 'rgba(244, 63, 94, 0.35)',
        text: 'text-rose-400',
        badge: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
        Icon: ShieldAlert,
        label: 'CRITICAL RISK',
      };
    }
    if (normalizedScore >= 35 || (riskLevel && riskLevel.toUpperCase() === 'MEDIUM')) {
      return {
        stroke: '#f59e0b',
        glow: 'rgba(245, 158, 11, 0.35)',
        text: 'text-amber-400',
        badge: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
        Icon: AlertTriangle,
        label: 'MODERATE RISK',
      };
    }
    return {
      stroke: '#10b981',
      glow: 'rgba(16, 185, 129, 0.35)',
      text: 'text-emerald-400',
      badge: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
      Icon: ShieldCheck,
      label: 'LOW RISK',
    };
  };

  const config = getColorConfig();
  const IconComponent = config.Icon;

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="relative flex flex-col items-center justify-center p-6 bg-slate-900/80 border border-slate-800 rounded-2xl backdrop-blur-md shadow-2xl"
    >
      <div className="relative flex items-center justify-center">
        <div 
          className="absolute w-40 h-40 rounded-full blur-3xl pointer-events-none transition-all duration-700"
          style={{ background: config.glow }}
        />

        <svg className="w-48 h-48 transform -rotate-90" viewBox="0 0 160 160">
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke="currentColor"
            strokeWidth="10"
            className="text-slate-800"
            fill="transparent"
          />
          <motion.circle
            cx="80"
            cy="80"
            r={radius}
            stroke={config.stroke}
            strokeWidth="10"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>

        <div className="absolute flex flex-col items-center justify-center text-center">
          <motion.span 
            className={`text-4xl font-extrabold tracking-tight ${config.text}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            key={normalizedScore}
          >
            {normalizedScore}
          </motion.span>
          <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
            Score / 100
          </span>
        </div>
      </div>

      <div className="mt-4 flex items-center gap-2">
        <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${config.badge}`}>
          <IconComponent className="w-3.5 h-3.5" />
          <span>{config.label}</span>
        </div>
      </div>

      <p className="mt-2 text-xs text-slate-400">
        Based on <span className="font-semibold text-slate-200">{reportCount}</span> verified incident report{reportCount === 1 ? '' : 's'}
      </p>
    </motion.div>
  );
}