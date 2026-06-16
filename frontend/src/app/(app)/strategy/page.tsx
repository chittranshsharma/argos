"use client";

import { useEffect, useState } from "react";
import { getStrategyPortfolio } from "@/lib/api";
import { Briefcase, Activity, AlertCircle, ArrowUpRight, ArrowDownRight, RefreshCw, BarChart } from "lucide-react";
import Link from "next/link";

export default function StrategyPage() {
  const [hypotheses, setHypotheses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const data = await getStrategyPortfolio();
      setHypotheses(data);
      setLoading(false);
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="skeleton h-12 w-64 mb-6" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="skeleton h-96 w-full" />
          <div className="skeleton h-96 w-full" />
          <div className="skeleton h-96 w-full" />
        </div>
      </div>
    );
  }

  // Filter only ACTIVE hypotheses
  const activeHypotheses = hypotheses.filter(h => h.status === 'ACTIVE');

  // Highest Momentum (Sorted by velocity)
  const highestMomentum = [...activeHypotheses].sort((a, b) => (b.confidence_velocity || 0) - (a.confidence_velocity || 0)).slice(0, 5);

  // Group by Type
  const typeGroups = activeHypotheses.reduce((acc, curr) => {
    const t = curr.type || 'UNKNOWN';
    if (!acc[t]) acc[t] = [];
    acc[t].push(curr);
    return acc;
  }, {} as Record<string, any[]>);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-on-surface flex items-center gap-3">
          <Briefcase className="w-8 h-8 text-primary" />
          Strategy Portfolio
        </h1>
        <p className="text-on-surface-variant mt-2 max-w-2xl">
          Market-level view of active strategic hypotheses across all tracked entities.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Momentum Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <div className="intelligence-card p-5 border-l-4 border-l-primary">
            <h3 className="text-sm font-mono text-on-surface-variant uppercase tracking-widest mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4" /> Highest Momentum
            </h3>
            
            <div className="space-y-4">
              {highestMomentum.length > 0 ? highestMomentum.map((h, i) => (
                <div key={i} className="flex flex-col gap-1 pb-3 border-b border-surface-bright/20 last:border-0 last:pb-0">
                  <div className="flex justify-between items-start">
                    <Link href={`/companies/${h.company_id}`} className="font-bold text-on-surface hover:text-primary transition-colors">
                      {h.companies?.name || 'Unknown'}
                    </Link>
                    <span className="flex items-center gap-1 text-xs font-bold text-status-success font-mono">
                      <ArrowUpRight className="w-3 h-3" />
                      +{Math.round((h.confidence_velocity || 0) * 100)}%
                    </span>
                  </div>
                  <div className="text-xs text-on-surface-variant line-clamp-1">{h.title}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] uppercase font-mono tracking-widest bg-surface-lowest px-1.5 py-0.5 rounded text-primary">
                      {Math.round(h.confidence * 100)}% CONF
                    </span>
                  </div>
                </div>
              )) : (
                <div className="text-sm text-on-surface-variant">No active hypotheses with momentum.</div>
              )}
            </div>
          </div>
        </div>

        {/* Narrative Columns */}
        <div className="lg:col-span-3">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {Object.keys(typeGroups).sort().map(type => (
              <div key={type} className="flex flex-col gap-4">
                <h3 className="text-xs font-bold font-mono text-on-surface-variant uppercase tracking-widest flex items-center justify-between border-b border-surface-bright/20 pb-2">
                  <span>{type.replace(/_/g, ' ')}</span>
                  <span className="bg-surface-bright/20 px-2 py-0.5 rounded text-on-surface">{typeGroups[type].length}</span>
                </h3>
                
                <div className="space-y-3">
                  {typeGroups[type].sort((a, b) => b.confidence - a.confidence).map(h => (
                    <div key={h.id} className="glass-panel p-4 rounded-xl border border-surface-bright/10 hover:border-surface-bright/30 transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <Link href={`/companies/${h.company_id}`} className="font-semibold text-on-surface hover:text-primary transition-colors">
                          {h.companies?.name || 'Unknown'}
                        </Link>
                        <span className={`text-xs font-bold font-mono ${h.confidence >= 0.7 ? 'text-status-success' : 'text-primary'}`}>
                          {Math.round(h.confidence * 100)}%
                        </span>
                      </div>
                      <p className="text-sm text-on-surface-variant line-clamp-2">{h.title}</p>
                      
                      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-surface-bright/10">
                        {h.drift_status === 'STALE' && (
                          <span className="flex items-center gap-1 text-[10px] font-mono text-status-error uppercase bg-status-error/10 px-1.5 py-0.5 rounded">
                            <AlertCircle className="w-3 h-3" /> STALE
                          </span>
                        )}
                        {h.drift_status === 'AGING' && (
                          <span className="flex items-center gap-1 text-[10px] font-mono text-status-elevated uppercase bg-status-elevated/10 px-1.5 py-0.5 rounded">
                            <RefreshCw className="w-3 h-3" /> AGING
                          </span>
                        )}
                        {h.drift_status === 'ACTIVE' && (
                          <span className="flex items-center gap-1 text-[10px] font-mono text-status-success uppercase bg-status-success/10 px-1.5 py-0.5 rounded">
                            <Activity className="w-3 h-3" /> ACTIVE
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
