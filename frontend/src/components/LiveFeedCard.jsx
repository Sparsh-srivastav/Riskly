import React from 'react';
import { motion } from 'framer-motion';
import { Flame, Phone, Mail, Clock, AlertOctagon } from 'lucide-react';

export default function LiveFeedCard({ item, index = 0 }) {
  const score = item.ml_risk_score ?? item.score;
  const isAlert = item.event === 'risk_alert' || item.type === 'alert' || (score !== undefined && score >= 70);

  const getTypeIcon = () => {
    if (item.contact_type === 'email') return <Mail className="w-3.5 h-3.5" />;
    if (item.contact_type === 'phone') return <Phone className="w-3.5 h-3.5" />;
    return <AlertOctagon className="w-3.5 h-3.5" />;
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.25, delay: Math.min(index * 0.03, 0.3) }}
      className={`p-3.5 rounded-xl border backdrop-blur-sm transition-all duration-200 ${
        isAlert
          ? 'bg-rose-950/20 border-rose-800/40 hover:border-rose-700/60'
          : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className={`p-1.5 rounded-lg ${isAlert ? 'bg-rose-500/20 text-rose-400' : 'bg-slate-800 text-slate-300'}`}>
            {isAlert ? <Flame className="w-4 h-4 animate-pulse" /> : getTypeIcon()}
          </div>
          <div>
            <span className="font-mono text-xs font-semibold text-slate-200">
              {item.contact_value || item.identifier || 'Unknown Target'}
            </span>
            <div className="flex items-center gap-2 text-[10px] text-slate-400">
              <span className="capitalize">{item.report_type || item.category || 'Incident'}</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Clock className="w-2.5 h-2.5" />
                {item.created_at ? new Date(item.created_at).toLocaleTimeString() : 'Just now'}
              </span>
            </div>
          </div>
        </div>

        {score !== undefined && (
          <div className={`text-right font-mono text-xs font-bold px-2 py-0.5 rounded border ${
            score >= 70
              ? 'text-rose-400 bg-rose-500/10 border-rose-500/30'
              : score >= 35
              ? 'text-amber-400 bg-amber-500/10 border-amber-500/30'
              : 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
          }`}>
            {score} / 100
          </div>
        )}
      </div>

      {item.description && (
        <p className="mt-2 text-xs text-slate-300 line-clamp-2 leading-relaxed">
          {item.description}
        </p>
      )}
    </motion.div>
  );
}
