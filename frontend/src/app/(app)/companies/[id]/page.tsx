"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getCompanyDetail, triggerMonitoring, getCompanyAnalytics, getRankings } from "@/lib/api";
import type { CompanyDetailResponse, CompanyAnalytics } from "@/lib/types";
import SignalFeed from "@/components/SignalFeed";
import { ArrowLeft, RefreshCw, Activity, ExternalLink, Globe, Play, FileText, BarChart3, AlertCircle, Network } from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ExecutiveMovements } from "@/components/ExecutiveMovements";
import { StrategicAssessment } from "@/components/StrategicAssessment";
import KnowledgeGraph from "@/components/KnowledgeGraph";

export default function CompanyDetailPage() {
  const { id } = useParams() as { id: string };
  const [data, setData] = useState<CompanyDetailResponse | null>(null);
  const [activityFeed, setActivityFeed] = useState<import('@/lib/types').ActivityItem[]>([]);
  const [analytics, setAnalytics] = useState<CompanyAnalytics | null>(null);
  const [rank, setRank] = useState<number | null>(null);
  const [allCompanies, setAllCompanies] = useState<{ id: string; name: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [monitoring, setMonitoring] = useState(false);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [res, feedData, analyticsData, rankingsData] = await Promise.all([
          getCompanyDetail(id),
          import('@/lib/api').then(m => m.getActivityFeed(id)),
          getCompanyAnalytics(id),
          getRankings(100)
        ]);
        setData(res);
        setActivityFeed(feedData);
        setAnalytics(analyticsData);
        const myRank = rankingsData.find(r => r.id === id)?.rank;
        if (myRank) setRank(myRank);
      } catch (err) {
        console.error("Failed to load company detail", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  const handleMonitor = async () => {
    setMonitoring(true);
    try {
      await triggerMonitoring(id);
      // Wait a bit, then reload
      setTimeout(async () => {
        try {
          const res = await getCompanyDetail(id);
          setData(res);
        } catch (e) {}
      }, 2000);
    } catch (err) {
      console.error("Failed to trigger monitoring", err);
    } finally {
      setMonitoring(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="skeleton h-8 w-48 mb-6" />
        <div className="skeleton h-32 w-full" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 skeleton h-96" />
          <div className="skeleton h-96" />
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-12 text-center text-on-surface-variant">
        <AlertCircle className="w-12 h-12 mx-auto mb-4 opacity-20" />
        <p>Entity not found or system error.</p>
        <Link href="/companies" className="text-primary hover:underline mt-4 inline-block">Return to Entities</Link>
      </div>
    );
  }

  const { company, latest_report, recent_signals } = data;

  const score = company.intelligence_score || analytics?.current?.total || 0;
  const signalsCount = company.signals_count || recent_signals.length;
  
  let sentimentText = "Neutral";
  let sentimentColor = "text-status-elevated";
  let sentimentBorder = "border-l-status-elevated";
  const sentValue = analytics?.current?.sentiment || 7.5;
  if (sentValue >= 10) {
    sentimentText = "Positive";
    sentimentColor = "text-status-success";
    sentimentBorder = "border-l-status-success";
  } else if (sentValue <= 5) {
    sentimentText = "Negative";
    sentimentColor = "text-status-error";
    sentimentBorder = "border-l-status-error";
  }

  const rankDisplay = rank ? `#${rank}` : "--";

  return (
    <div className="space-y-6">
      <Link href="/companies" className="inline-flex items-center gap-2 text-sm text-on-surface-variant hover:text-primary transition-colors">
        <ArrowLeft className="w-4 h-4" />
        Back to Entities
      </Link>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold tracking-tight text-on-surface uppercase">{company.name}</h1>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-status-success/10 text-status-success border border-status-success/20">
                Active Target
              </span>
            </div>
            <div className="text-sm text-on-surface-variant mt-1 font-medium">
              Global Technology & Services
            </div>
          <div className="flex items-center gap-4 mt-2 text-sm text-on-surface-variant">
            {company.website && (
              <a href={company.website} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 hover:text-primary transition-colors">
                <Globe className="w-4 h-4" /> {company.website.replace(/^https?:\/\//, '')}
              </a>
            )}
            {company.github_org && (
              <a href={`https://github.com/${company.github_org}`} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 hover:text-primary transition-colors">
                <Activity className="w-4 h-4" /> GitHub: {company.github_org}
              </a>
            )}
            <span className="flex items-center gap-1.5">
              <RefreshCw className="w-4 h-4" />
              Last scan: {company.last_monitored ? new Date(company.last_monitored).toLocaleString() : "Never"}
            </span>
          </div>
        </div>

        <button 
          onClick={handleMonitor}
          disabled={monitoring}
          className="flex items-center gap-2 bg-primary text-black font-bold px-5 py-2.5 rounded-lg hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50"
        >
          {monitoring ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          {monitoring ? "Scanning..." : "Force Scan"}
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
        <div className="intelligence-card p-4 border-l-2 border-l-primary relative group cursor-default">
          <div className="text-xs font-mono text-on-surface-variant uppercase tracking-widest mb-1">Activity Score</div>
          <div className="text-3xl font-bold text-on-surface">{score}</div>
        </div>
        <div className="intelligence-card p-4 border-l-2 border-l-surface-bright/50">
          <div className="text-xs font-mono text-on-surface-variant uppercase tracking-widest mb-1">Tracked Signals</div>
          <div className="text-3xl font-bold text-on-surface">{signalsCount}</div>
        </div>
        <div className={`intelligence-card p-4 border-l-2 ${sentimentBorder}`}>
          <div className="text-xs font-mono text-on-surface-variant uppercase tracking-widest mb-1">Sentiment</div>
          <div className={`text-3xl font-bold ${sentimentColor}`}>{sentimentText}</div>
        </div>
        <div className="intelligence-card p-4 border-l-2 border-l-surface-bright/50">
          <div className="text-xs font-mono text-on-surface-variant uppercase tracking-widest mb-1">Network Rank</div>
          <div className="text-3xl font-bold text-on-surface">{rankDisplay}</div>
        </div>
      </div>

      {data.score_breakdown && (
        <div className="mt-6 bg-surface-low border border-surface-bright/20 p-5 rounded-xl">
          <h3 className="text-sm font-mono uppercase font-bold text-on-surface tracking-wider mb-4 border-b border-surface-bright/20 pb-2 flex justify-between">
            <span>Score Components</span>
            <span className="text-primary">Total: {data.score_breakdown.total.toFixed(1)}</span>
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-xs font-mono">
            <div className="flex flex-col gap-1">
              <span className="text-on-surface-variant">Signal Volume</span>
              <span className="text-lg font-bold text-on-surface">{data.score_breakdown.signal_volume.toFixed(1)}</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-on-surface-variant">Hiring Activity</span>
              <span className="text-lg font-bold text-on-surface">{data.score_breakdown.hiring_velocity.toFixed(1)}</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-on-surface-variant">Funding Activity</span>
              <span className="text-lg font-bold text-on-surface">{data.score_breakdown.funding_activity.toFixed(1)}</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-on-surface-variant">Sentiment</span>
              <span className="text-lg font-bold text-on-surface">{data.score_breakdown.sentiment.toFixed(1)}</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-on-surface-variant">Exec Events</span>
              <span className="text-lg font-bold text-on-surface">{data.score_breakdown.executive_events.toFixed(1)}</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-on-surface-variant">Reports</span>
              <span className="text-lg font-bold text-on-surface">{data.score_breakdown.report_activity.toFixed(1)}</span>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-4">
        {/* Main Feed */}
        <div className="lg:col-span-2 space-y-8">
          
          <StrategicAssessment companyId={id} />

          <ExecutiveMovements companyId={id} />

          <div className="space-y-4">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-lg font-semibold tracking-tight text-on-surface flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary" /> Intelligence Feed
              </h2>
            </div>
          
          {activityFeed.length > 0 ? (
            <SignalFeed signals={activityFeed} showCompany={false} />
          ) : (
            <div className="glass-panel p-8 text-center rounded-xl border border-surface-bright/20">
              <p className="text-on-surface-variant">No activity intercepted yet.</p>
            </div>
          )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="intelligence-card p-5">
            <h3 className="text-sm font-mono text-on-surface-variant uppercase tracking-widest mb-4 flex items-center gap-2">
              <FileText className="w-4 h-4" /> Latest Briefing
            </h3>
            
            {latest_report ? (
              <div className="space-y-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold text-on-surface">{latest_report.company_name} Briefing</h4>
                  <span className="text-xs text-on-surface-variant whitespace-nowrap ml-2">
                    {new Date(latest_report.generated_at).toLocaleDateString()}
                  </span>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h5 className="text-[10px] font-bold text-primary uppercase tracking-widest mb-1.5">Executive Summary</h5>
                    <p className="text-sm text-on-surface-variant leading-relaxed line-clamp-3">
                      {latest_report.report_markdown.replace(/[#*`]/g, '').substring(0, 200)}...
                    </p>
                  </div>
                  <div>
                    <h5 className="text-[10px] font-bold text-primary uppercase tracking-widest mb-1.5">Key Findings</h5>
                    <ul className="text-sm text-on-surface-variant list-disc pl-4 space-y-1">
                      <li>Hiring velocity increased steadily</li>
                      <li>Acquisition activity detected in AI sector</li>
                      <li>New open source initiative announced</li>
                    </ul>
                  </div>
                  <div className="flex gap-6 pt-3 border-t border-surface-bright/20">
                    <div>
                      <h5 className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Risk Assessment</h5>
                      <span className="text-sm text-status-elevated font-medium">Medium</span>
                    </div>
                    <div>
                      <h5 className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Market Outlook</h5>
                      <span className="text-sm text-status-success font-medium">Positive</span>
                    </div>
                  </div>
                </div>

                <Link 
                  href="/reports" 
                  className="flex items-center justify-center w-full gap-2 text-sm bg-surface-lowest border border-surface-bright/30 py-2 rounded text-on-surface hover:text-primary transition-colors font-medium mt-4"
                >
                  View Full Report <ExternalLink className="w-4 h-4" />
                </Link>
              </div>
            ) : (
              <div className="text-sm text-on-surface-variant text-center py-4">
                No intelligence briefings generated yet.
              </div>
            )}
          </div>

          <div className="intelligence-card p-5">
             <h3 className="text-sm font-mono text-on-surface-variant uppercase tracking-widest mb-4 flex items-center gap-2">
              <BarChart3 className="w-4 h-4" /> Threat Matrix
            </h3>
            {/* Analytics Breakdown */}
              <div className="space-y-4">
                {(analytics?.current ? [
                  { label: "Signal Volume", value: `${analytics.current.signal_volume}/25`, score: (analytics.current.signal_volume/25)*100, color: "bg-primary", text: "text-primary" },
                  { label: "Hiring Velocity", value: `${analytics.current.hiring_velocity}/18`, score: (analytics.current.hiring_velocity/18)*100, color: "bg-status-success", text: "text-status-success" },
                  { label: "Funding Activity", value: `${analytics.current.funding_activity}/20`, score: (analytics.current.funding_activity/20)*100, color: "bg-primary", text: "text-primary" },
                  { label: "Sentiment Score", value: `${analytics.current.sentiment}/15`, score: (analytics.current.sentiment/15)*100, color: "bg-status-elevated", text: "text-status-elevated" },
                  { label: "Executive Events", value: `${analytics.current.executive_events}/8`, score: (analytics.current.executive_events/8)*100, color: "bg-status-error", text: "text-status-error" },
                  { label: "Report Activity", value: `${analytics.current.report_activity}/5`, score: (analytics.current.report_activity/5)*100, color: "bg-primary", text: "text-primary" }
                ] : [
                  { label: "Data Pending", value: "-", score: 0, color: "bg-surface-bright", text: "text-on-surface-variant" }
                ]).map((metric, i) => (
                  <div key={i} className="flex flex-col gap-1.5">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-on-surface-variant font-medium">{metric.label}</span>
                      <span className={`${metric.text} font-mono text-xs`}>{metric.value}</span>
                    </div>
                    <div className="h-1.5 w-full bg-surface-bright/20 rounded-full overflow-hidden">
                      <div className={`h-full ${metric.color}`} style={{ width: `${metric.score}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="intelligence-card p-5">
              <h3 className="text-sm font-mono text-on-surface-variant uppercase tracking-widest mb-4 flex items-center gap-2">
                <Activity className="w-4 h-4" /> Activity Trend (30d)
              </h3>
              <div className="flex items-end gap-[2px] h-16 w-full mt-2">
                {(() => {
                  const activityTrend = analytics?.history?.slice(0, 30).reverse().map(h => h.payload_json.total) || [];
                  const maxTrend = activityTrend.length > 0 ? Math.max(100, ...activityTrend) : 100;
                  const trendBars = activityTrend.length > 0 ? activityTrend : Array(20).fill(0);
                  
                  return trendBars.map((val, i) => (
                    <div 
                      key={i} 
                      className="flex-1 bg-primary/40 hover:bg-primary transition-colors rounded-t-sm" 
                      style={{ height: `${(val / maxTrend) * 100}%` }} 
                      title={`Score: ${val}`}
                    />
                  ));
                })()}
              </div>
            </div>
        </div>
      </div>
    </div>
  );
}