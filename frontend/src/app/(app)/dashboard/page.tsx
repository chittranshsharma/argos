"use client";

import { useEffect, useState } from "react";
import { getStats, getSignalFeed, getShareOfVoice, getGlobalAnomalies, getSignalSources } from "@/lib/api";
import type { DashboardStats, Signal, ShareOfVoiceEntry, Alert } from "@/lib/types";
import SignalFeed from "@/components/SignalFeed";
import { Activity, Zap, FileText, Globe, Network, Brain, AlertTriangle, TrendingUp, RefreshCw, ArrowRight, Shield, Database, Plus, Search, Loader2, ExternalLink } from "lucide-react";

interface InsightCardProps {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
  trend?: string;
  status?: string;
  companyId?: string;
  companyName?: string;
}

// ── Stat Card ──────────────────────────────────────────────

function StatCard({
  label,
  value,
  metaText,
  metaColor,
  icon: Icon,
  color,
  delay,
}: {
  label: string;
  value: number | string;
  metaText: string;
  metaColor: string;
  icon: React.ElementType;
  color: string;
  delay: number;
}) {
  return (
    <div
      className="intelligence-card p-5 animate-slide-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="font-mono text-xs text-on-surface-variant uppercase tracking-widest mb-2">
            {label}
          </p>
          <div className="flex items-baseline gap-3">
            <p className={`text-3xl font-bold ${color}`}>{value}</p>
            <span className={`text-xs font-mono ${metaColor}`}>{metaText}</span>
          </div>
        </div>
        <div
          className={`flex h-10 w-10 items-center justify-center rounded-lg bg-surface-bright/20 border border-surface-bright/50 ${color}`}
        >
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
}

// ── Dashboard Page ─────────────────────────────────────────

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [signals, setSignals] = useState<import('@/lib/types').ActivityItem[]>([]);
  const [trending, setTrending] = useState<ShareOfVoiceEntry[]>([]);
  const [anomalies, setAnomalies] = useState<Alert[]>([]);
  const [sources, setSources] = useState<{ percentages: Record<string, number> } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsData, signalsData, trendingData, anomaliesData, sourcesData] = await Promise.all([
          getStats(),
          getSignalFeed({ limit: 20 }),
          getShareOfVoice(7), // past week
          getGlobalAnomalies(7), // past week
          getSignalSources()
        ]);
        setStats(statsData);
        setSignals(signalsData);
        setTrending(trendingData.slice(0, 5));
        setAnomalies(anomaliesData.slice(0, 3));
        setSources(sourcesData);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
        // Set defaults on error
        setStats({
          companies_tracked: 0,
          signals_today: 0,
          high_priority_alerts: 0,
          reports_generated: 0,
        });
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tighter text-on-surface">
          Command Center
        </h1>
        <p className="text-sm leading-relaxed text-on-surface-variant mt-1">
          Real-time competitive intelligence across all tracked entities.
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {loading ? (
          <>
            {[...Array(4)].map((_, i) => (
              <div key={i} className="skeleton h-[100px]" />
            ))}
          </>
        ) : (
          <>
            <StatCard
              label="Entities Tracked"
              value={stats?.companies_tracked ?? 3}
              metaText="+1 this week"
              metaColor="text-status-success"
              icon={Globe}
              color="text-primary"
              delay={0}
            />
            <StatCard
              label="Signals Today"
              value={stats?.signals_today ?? 227}
              metaText="+18%"
              metaColor="text-status-success"
              icon={Activity}
              color="text-status-success"
              delay={80}
            />
            <StatCard
              label="Critical Alerts"
              value={stats?.high_priority_alerts ?? 0}
              metaText="No action needed"
              metaColor="text-on-surface-variant"
              icon={Zap}
              color="text-status-critical"
              delay={160}
            />
            <StatCard
              label="Generated Reports"
              value={stats?.reports_generated ?? 5}
              metaText="2 scheduled"
              metaColor="text-on-surface-variant"
              icon={FileText}
              color="text-status-elevated"
              delay={240}
            />
          </>
        )}
      </div>

      {/* Live Signal Feed & Trending Topics (Grid) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-semibold tracking-tight text-on-surface">
              Intelligence Stream
            </h2>
            <div className="flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-status-success/10 border border-status-success/20">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-status-success opacity-75" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-status-success" />
              </span>
              <span className="text-[10px] font-mono text-status-success uppercase font-bold tracking-wider">Live</span>
            </div>
          </div>

          {loading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="skeleton h-[120px]" />
              ))}
            </div>
          ) : (
            <SignalFeed signals={signals} showCompany={true} />
          )}
        </div>

        {/* Sidebar Widgets */}
        <div className="space-y-6">
          <div className="intelligence-card p-6">
            <h3 className="text-sm font-mono text-on-surface-variant uppercase tracking-widest mb-4">Trending Entities</h3>
            <div className="space-y-4">
              {loading ? (
                <div className="text-xs text-on-surface-variant">LOADING...</div>
              ) : trending.length === 0 ? (
                <div className="text-xs text-on-surface-variant">NO TRENDING DATA</div>
              ) : trending.map((topic, i) => (
                <div key={topic.company} className="flex flex-col gap-1.5 group cursor-pointer">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-on-surface hover:text-primary transition-colors font-medium truncate max-w-[150px]">{topic.company}</span>
                    <span className="font-mono text-xs text-primary">{topic.percentage}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-surface-bright/20 rounded-full overflow-hidden">
                    <div className="h-full bg-primary group-hover:bg-primary-hover transition-colors" style={{ width: `${topic.percentage}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="intelligence-card p-6">
            <h3 className="text-sm font-mono text-on-surface-variant uppercase tracking-widest mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4" /> System Anomalies
            </h3>
            <div className="flex flex-col gap-3">
              {loading ? (
                <div className="text-xs text-on-surface-variant">LOADING...</div>
              ) : anomalies.length === 0 ? (
                <div className="text-xs text-on-surface-variant">NO SYSTEM ANOMALIES DETECTED</div>
              ) : anomalies.map((anomaly) => (
                <div key={anomaly.id} className={`p-3 border rounded-lg flex gap-3 ${anomaly.impact_level === 'Critical' ? 'bg-status-critical/10 border-status-critical/20' : 'bg-surface-lowest border-surface-bright/20'}`}>
                  <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${anomaly.impact_level === 'Critical' ? 'bg-status-critical animate-pulse' : 'bg-status-elevated'}`} />
                  <div>
                    <div className={`text-sm font-semibold ${anomaly.impact_level === 'Critical' ? 'text-status-critical' : 'text-on-surface'}`}>
                      {anomaly.alert_type.replace(/_/g, ' ')}
                    </div>
                    <div className={`text-xs ${anomaly.impact_level === 'Critical' ? 'text-status-critical/70' : 'text-on-surface-variant'}`}>
                      {anomaly.company_name} - Score {anomaly.confidence_score ? `${anomaly.confidence_score}%` : 'N/A'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="intelligence-card p-6">
            <h3 className="text-sm font-mono text-on-surface-variant uppercase tracking-widest mb-4 flex items-center gap-2">
              <Network className="w-4 h-4" /> Signal Sources
            </h3>
            <div className="flex flex-col gap-3">
              {loading ? (
                <div className="text-xs text-on-surface-variant">LOADING...</div>
              ) : !sources || Object.keys(sources.percentages).length === 0 ? (
                <div className="text-xs text-on-surface-variant">NO SOURCE DATA DETECTED</div>
              ) : Object.entries(sources.percentages).sort((a, b) => b[1] - a[1]).map(([agent, pct]) => (
                <div key={agent} className="flex flex-col gap-1.5 group cursor-pointer">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-on-surface hover:text-primary transition-colors font-medium truncate max-w-[150px]">{agent}</span>
                    <span className="font-mono text-xs text-primary">{pct}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-surface-bright/20 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 group-hover:bg-blue-400 transition-colors" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}