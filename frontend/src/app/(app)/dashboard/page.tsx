"use client";

import { useEffect, useState } from "react";
import { getStats, getSignalFeed, getShareOfVoice, getGlobalAnomalies, getSignalSources, getCompanies } from "@/lib/api";
import type { DashboardStats, ShareOfVoiceEntry, Alert, Company } from "@/lib/types";
import SignalFeed from "@/components/SignalFeed";
import { Activity, Zap, FileText, Globe, Network, Brain, AlertTriangle, TrendingUp, RefreshCw, ArrowRight, Shield, Database, Plus, Search, Loader2, ExternalLink } from "lucide-react";
import Link from "next/link";

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

function InsightCard({ title, value, description, icon, trend, status, companyId, companyName }: InsightCardProps) {
  return (
    <div className="bg-surface-lowest/50 border border-surface-bright/20 rounded-2xl p-6 flex flex-col justify-between h-full hover:border-primary/30 transition-all duration-200">
      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-mono uppercase tracking-widest text-on-surface-variant">{title}</span>
          <div className="p-2 rounded-lg bg-surface-bright/10 text-primary">{icon}</div>
        </div>
        <h3 className="text-lg font-bold text-on-surface mb-1 leading-snug">{value}</h3>
        <p className="text-sm text-on-surface-variant mb-4">{description}</p>
      </div>
      {companyId && (
        <Link
          href={`/companies/${companyId}`}
          className="flex items-center gap-1.5 text-xs text-primary hover:text-primary-hover font-medium transition-colors mt-auto pt-2 group"
        >
          View Entity <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
        </Link>
      )}
    </div>
  );
}

function getBriefingText(companies: Company[], stats: DashboardStats | null, signals: import('@/lib/types').ActivityItem[]) {
  const signalCount = stats?.signals_today ?? signals.length;
  const entitiesCount = companies.length;
  return `${signalCount} signals intercepted recently across ${entitiesCount} tracked entities. 3 hypotheses strengthened, 1 weakened. Anthropic generated the highest intelligence velocity.`;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [signals, setSignals] = useState<import('@/lib/types').ActivityItem[]>([]);
  const [trending, setTrending] = useState<ShareOfVoiceEntry[]>([]);
  const [anomalies, setAnomalies] = useState<Alert[]>([]);
  const [sources, setSources] = useState<{ percentages: Record<string, number> } | null>(null);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsData, signalsData, trendingData, anomaliesData, sourcesData, companiesData] = await Promise.all([
          getStats(),
          getSignalFeed({ limit: 20 }),
          getShareOfVoice(7),
          getGlobalAnomalies(7),
          getSignalSources(),
          getCompanies()
        ]);
        setStats(statsData);
        setSignals(signalsData);
        setTrending(trendingData.slice(0, 5));
        setAnomalies(anomaliesData.slice(0, 3));
        setSources(sourcesData);
        setCompanies(companiesData);
      } catch (err) {
        print("Dashboard fetch error:", err);
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

  const openaiCompany = companies.find(c => c.name.toLowerCase() === 'openai');
  const stripeCompany = companies.find(c => c.name.toLowerCase() === 'stripe');
  const anthropicCompany = companies.find(c => c.name.toLowerCase() === 'anthropic');

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tighter text-on-surface">
          Intelligence Briefing
        </h1>
        <p className="text-sm leading-relaxed text-on-surface-variant mt-2 max-w-3xl">
          {loading ? (
            <span className="inline-block skeleton h-4 w-96 rounded" />
          ) : (
            getBriefingText(companies, stats, signals)
          )}
        </p>
      </div>

      {/* Focus Areas (Insights) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {loading ? (
          <>
            {[...Array(3)].map((_, i) => (
              <div key={i} className="skeleton h-[180px]" />
            ))}
          </>
        ) : (
          <>
            <InsightCard
              title="Biggest Strategic Shift"
              value="OpenAI"
              description="Hiring expansion and news signal volume increased activity score to 92. 2 active hypotheses updated."
              icon={<TrendingUp className="w-5 h-5 text-status-success" />}
              companyId={openaiCompany?.id}
              companyName="OpenAI"
            />
            <InsightCard
              title="Hypothesis Under Pressure"
              value="Stripe AI Payments Expansion"
              description="Counter-evidence signals detected. Integration timeline constraints identified in developer forums."
              icon={<Brain className="w-5 h-5 text-status-elevated" />}
              companyId={stripeCompany?.id}
              companyName="Stripe"
            />
            <InsightCard
              title="Entity Requiring Review"
              value="Anthropic"
              description="Critical system anomaly alert flagged. Competitor tracking reports require active validation."
              icon={<AlertTriangle className="w-5 h-5 text-status-critical animate-pulse" />}
              companyId={anthropicCompany?.id}
              companyName="Anthropic"
            />
          </>
        )}
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-semibold tracking-tight text-on-surface">
              Strategic Developments
            </h2>
            <div className="flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-status-success/10 border border-status-success/20">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-status-success opacity-75" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-status-success" />
              </span>
              <span className="text-[10px] font-mono text-status-success uppercase font-bold tracking-wider">Live Feed</span>
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
              ) : trending.map((topic) => (
                <Link key={topic.company} href={`/companies/${companies.find(c => c.name.toLowerCase() === topic.company.toLowerCase())?.id || ''}`} className="flex flex-col gap-1.5 group cursor-pointer block">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-on-surface group-hover:text-primary transition-colors font-medium truncate max-w-[150px]">{topic.company}</span>
                    <span className="font-mono text-xs text-primary">{topic.percentage}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-surface-bright/20 rounded-full overflow-hidden">
                    <div className="h-full bg-primary group-hover:bg-primary-hover transition-colors" style={{ width: `${topic.percentage}%` }} />
                  </div>
                </Link>
              ))}
            </div>
          </div>

          <div className="intelligence-card p-6">
            <h3 className="text-sm font-mono text-on-surface-variant uppercase tracking-widest mb-4 flex items-center gap-2">
              <Brain className="w-4 h-4" /> Active Hypotheses
            </h3>
            <div className="flex flex-col gap-3">
              {loading ? (
                <div className="text-xs text-on-surface-variant">LOADING...</div>
              ) : companies.length === 0 ? (
                <div className="text-xs text-on-surface-variant">NO ACTIVE HYPOTHESES</div>
              ) : companies.map((company) => (
                <Link key={company.id} href={`/companies/${company.id}`} className="p-3 border rounded-lg flex items-center justify-between bg-surface-lowest border-surface-bright/20 hover:border-primary/30 transition-colors block">
                  <div className="text-sm font-semibold text-on-surface">
                    {company.name}
                  </div>
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">
                    {company.signals_count || 0} signals
                  </span>
                </Link>
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
                <div key={agent} className="flex flex-col gap-1.5 group">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-on-surface font-medium truncate max-w-[150px]">{agent}</span>
                    <span className="font-mono text-xs text-primary">{pct}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-surface-bright/20 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 transition-colors" style={{ width: `${pct}%` }} />
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
