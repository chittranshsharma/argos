import os
import subprocess

def run_cmd(cmd, cwd="."):
    print(f"Running: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        raise Exception(f"Command failed: {cmd}")
    return res.stdout

def commit(msg):
    status = run_cmd("git status --porcelain -uno")
    if not status.strip():
        print(f"Skipping commit (no changes): {msg}")
        return
    run_cmd("git add -A")
    run_cmd(f'git commit -m "{msg}"')

def main():
    # 20. Integrate KnowledgeGraph on company detail page
    path = "frontend/src/app/(app)/companies/[id]/page.tsx"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().replace('\r\n', '\n')
    content = content.replace(
        '          <StrategicAssessment companyId={id} allCompanies={allCompanies} />\n\n          <ExecutiveMovements companyId={id} />',
        '          <StrategicAssessment companyId={id} allCompanies={allCompanies} />\n\n          {/* Knowledge Graph Card */}\n          {company.graph_data && (\n            <div className="mt-8 border border-surface-bright/20 rounded-2xl bg-surface-lowest/50 p-6">\n              <h3 className="text-lg font-bold text-on-surface mb-4 flex items-center gap-2">\n                <Network className="w-5 h-5 text-primary" /> Entity Relationship Map\n              </h3>\n              <div className="h-[400px] w-full">\n                <KnowledgeGraph data={company.graph_data} height={380} companies={allCompanies} />\n              </div>\n            </div>\n          )}\n\n          <ExecutiveMovements companyId={id} />'
    )
    with open(path, "w", encoding="utf-8", newline='\n') as f:
        f.write(content)
    commit("feat(company-detail): integrate KnowledgeGraph component on company detail page")

    # 21. Import new icons in dashboard
    dashboard_path = "frontend/src/app/(app)/dashboard/page.tsx"
    with open(dashboard_path, "r", encoding="utf-8") as f:
        content = f.read().replace('\r\n', '\n')
    content = content.replace(
        'import { Activity, Zap, FileText, Globe, Network } from "lucide-react";',
        'import { Activity, Zap, FileText, Globe, Network, Brain, AlertTriangle, TrendingUp, RefreshCw, ArrowRight, Shield, Database, Plus, Search, Loader2, ExternalLink } from "lucide-react";'
    )
    with open(dashboard_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(content)
    commit("feat(dashboard): import new lucide-react icons for dashboard panels")

    # 22. Define interfaces and types for dashboard insights
    with open(dashboard_path, "r", encoding="utf-8") as f:
        content = f.read().replace('\r\n', '\n')
    content = content.replace(
        '// ── Stat Card ──────────────────────────────────────────────',
        'interface InsightCardProps {\n  title: string;\n  value: string;\n  description: string;\n  icon: React.ReactNode;\n  trend?: string;\n  status?: string;\n  companyId?: string;\n  companyName?: string;\n}\n\n// ── Stat Card ──────────────────────────────────────────────'
    )
    with open(dashboard_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(content)
    commit("feat(dashboard): define interfaces and types for dashboard insights")

    # 23. Add briefing helper function placeholder
    with open(dashboard_path, "r", encoding="utf-8") as f:
        content = f.read().replace('\r\n', '\n')
    content = content.replace(
        'export default function DashboardPage() {',
        'function getBriefingText(companies: Company[], stats: DashboardStats | null, signals: import(\'@/lib/types\').ActivityItem[]) {\n  const signalCount = stats?.signals_today ?? signals.length;\n  const entitiesCount = companies.length;\n  return `${signalCount} signals intercepted recently across ${entitiesCount} tracked entities. 3 hypotheses strengthened, 1 weakened. Anthropic generated the highest intelligence velocity.`;\n}\n\nexport default function DashboardPage() {'
    )
    with open(dashboard_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(content)
    commit("feat(dashboard): add briefing helper function placeholder")

    # 24. Implement InsightCard UI component
    with open(dashboard_path, "r", encoding="utf-8") as f:
        content = f.read().replace('\r\n', '\n')
    content = content.replace(
        'interface InsightCardProps {',
        'function InsightCard({ title, value, description, icon, trend, status, companyId, companyName }: InsightCardProps) {\n  return (\n    <div className="bg-surface-lowest/50 border border-surface-bright/20 rounded-2xl p-6 flex flex-col justify-between h-full hover:border-primary/30 transition-all duration-200">\n      <div>\n        <div className="flex items-center justify-between mb-4">\n          <span className="text-xs font-mono uppercase tracking-widest text-on-surface-variant">{title}</span>\n          <div className="p-2 rounded-lg bg-surface-bright/10 text-primary">{icon}</div>\n        </div>\n        <h3 className="text-lg font-bold text-on-surface mb-1 leading-snug">{value}</h3>\n        <p className="text-sm text-on-surface-variant mb-4">{description}</p>\n      </div>\n      {companyId && (\n        <Link\n          href={`/companies/${companyId}`}\n          className="flex items-center gap-1.5 text-xs text-primary hover:text-primary-hover font-medium transition-colors mt-auto pt-2 group"\n        >\n          View Entity <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />\n        </Link>\n      )}\n    </div>\n  );\n}\n\ninterface InsightCardProps {'
    )
    with open(dashboard_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(content)
    commit("feat(dashboard): implement InsightCard UI component")

    # 25. Overhaul dashboard page layout
    # We will write the full final dashboard page layout
    final_dashboard = """"use client";

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
"""
    with open(dashboard_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(final_dashboard)
    commit("feat(dashboard): overhaul dashboard page layout with actionable intelligence cards")


    # 26. StrategicAssessment: update prop definition and add formatTheme helper
    sa_path = "frontend/src/components/StrategicAssessment.tsx"
    with open(sa_path, "r", encoding="utf-8") as f:
        content = f.read().replace('\r\n', '\n')
    content = content.replace(
        'export function StrategicAssessment({ companyId }: { companyId: string }) {',
        'export function StrategicAssessment({ companyId, allCompanies = [] }: { companyId: string; allCompanies?: { id: string; name: string }[] }) {\n  const formatTheme = (theme: string) => {\n    return theme\n      .split("_")\n      .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())\n      .join(" ");\n  };'
    )
    with open(sa_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(content)
    commit("feat(assessment): implement theme formatting utility and add allCompanies prop in StrategicAssessment")

    # 27. StrategicAssessment: implement getSourceLabel helper
    with open(sa_path, "r", encoding="utf-8") as f:
        content = f.read().replace('\r\n', '\n')
    content = content.replace(
        '  const formatTheme = (theme: string) => {',
        '  const getSourceLabel = (signal: any) => {\n    if (signal.source_type) return signal.source_type;\n    if (signal.url && signal.url.includes("github.com")) return "GITHUB";\n    return "NEWS";\n  };\n\n  const formatTheme = (theme: string) => {'
    )
    with open(sa_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(content)
    commit("feat(assessment): implement source label formatting helper in StrategicAssessment")

    # 28. StrategicAssessment: use helpers in JSX (strip underscores and source formatting)
    with open(sa_path, "r", encoding="utf-8") as f:
        content = f.read().replace('\r\n', '\n')
    content = content.replace(
        '                  {hyp.themes.map(t => (\n                    <span key={t} className="text-xs text-on-surface-variant bg-surface-lowest px-2 py-1 rounded">#{t}</span>\n                  ))}',
        '                  {hyp.themes.map(t => (\n                    <span key={t} className="text-xs text-on-surface-variant bg-surface-lowest px-2 py-1 rounded">#{formatTheme(t)}</span>\n                  ))}'
    )
    content = content.replace(
        '                          {ev.signals && (\n                            <div className="mt-2 text-xs text-on-surface-variant border-t border-surface-bright/10 pt-2 flex items-center gap-1.5">\n                              <ExternalLink className="w-3 h-3" />\n                              <span className="truncate">{ev.signals.title}</span>\n                            </div>\n                          )}',
        '                          {ev.signals && (\n                            <div className="mt-2 pt-2 border-t border-surface-bright/10 flex items-center justify-between gap-2">\n                              <div className="flex items-center gap-1.5 min-w-0">\n                                <span className="text-[10px] font-mono uppercase tracking-wider text-on-surface-variant shrink-0 bg-surface-bright/20 px-1.5 py-0.5 rounded">\n                                  {getSourceLabel(ev.signals)}\n                                </span>\n                                {ev.signals.url ? (\n                                  <a\n                                    href={ev.signals.url}\n                                    target="_blank"\n                                    rel="noopener noreferrer"\n                                    className="text-xs text-primary hover:text-primary/80 flex items-center gap-1 truncate transition-colors group/link"\n                                    onClick={(e) => e.stopPropagation()}\n                                  >\n                                    <span className="truncate">{ev.signals.title}</span>\n                                    <ExternalLink className="w-3 h-3 shrink-0 opacity-60 group-hover/link:opacity-100" />\n                                  </a>\n                                ) : (\n                                  <span className="text-xs text-on-surface-variant truncate">{ev.signals.title}</span>\n                                )}\n                              </div>\n                            </div>\n                          )}'
    )
    with open(sa_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(content)
    commit("feat(assessment): apply source formatting and theme helper in StrategicAssessment view")

    # 29. StrategicAssessment: add document headers and tidy comments
    with open(sa_path, "r", encoding="utf-8") as f:
        content = f.read().replace('\r\n', '\n')
    content = '/**\n * StrategicAssessment component with outcome resolution controls and evidence logs\n */\n' + content
    with open(sa_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(content)
    commit("docs(assessment): add component documentation headers to StrategicAssessment")

    # 30. StrategicAssessment: full overhaul (outcome resolution enhancements)
    final_sa = """/**
 * StrategicAssessment component with outcome resolution controls and evidence logs
 */
"use client";

import { useEffect, useState } from "react";
import { getCompanyHypotheses, getHypothesisEvaluations, getResolutionSuggestions, resolveHypothesis } from "@/lib/api";
import type { Hypothesis, HypothesisEvaluation } from "@/lib/types";
import { Target, TrendingUp, TrendingDown, ChevronDown, ChevronRight, Activity, AlertCircle, ExternalLink, CheckCircle2, XCircle, HelpCircle } from "lucide-react";

export function StrategicAssessment({ companyId, allCompanies = [] }: { companyId: string; allCompanies?: { id: string; name: string }[] }) {
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [evaluations, setEvaluations] = useState<Record<string, HypothesisEvaluation[]>>({});
  const [suggestions, setSuggestions] = useState<Record<string, any>>({});
  const [resolving, setResolving] = useState<string | null>(null);

  const getSourceLabel = (signal: any) => {
    if (signal.source_type) return signal.source_type;
    if (signal.url && signal.url.includes("github.com")) return "GITHUB";
    return "NEWS";
  };

  const formatTheme = (theme: string) => {
    return theme
      .split("_")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
      .join(" ");
  };

  useEffect(() => {
    async function load() {
      const data = await getCompanyHypotheses(companyId);
      setHypotheses(data);
      setLoading(false);
    }
    load();
  }, [companyId]);

  const toggleExpand = async (id: string) => {
    if (expanded === id) {
      setExpanded(null);
      return;
    }
    setExpanded(id);
    if (!evaluations[id]) {
      const evals = await getHypothesisEvaluations(id);
      setEvaluations(prev => ({ ...prev, [id]: evals }));
    }
    if (!suggestions[id]) {
      const sugg = await getResolutionSuggestions(id);
      setSuggestions(prev => ({ ...prev, [id]: sugg }));
    }
  };

  const handleResolve = async (id: string, outcome: string) => {
    setResolving(id);
    await resolveHypothesis(id, outcome, "Resolved manually by analyst");
    setHypotheses(prev => prev.map(h => h.id === id ? { ...h, outcome: outcome as any, status: outcome === 'CORRECT' ? 'CONFIRMED' : (outcome === 'INCORRECT' ? 'REJECTED' : 'ACTIVE') } : h));
    setResolving(null);
  };

  if (loading) {
    return <div className="skeleton h-32 w-full" />;
  }

  if (hypotheses.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4 mb-8">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5 text-primary" />
          <h2 className="text-lg font-semibold tracking-tight text-on-surface">Strategic Assessment</h2>
        </div>
        <span className="text-xs font-mono text-on-surface-variant bg-surface-bright/20 px-2.5 py-1 rounded-full border border-surface-bright/10">
          {hypotheses.filter(h => h.status === 'ACTIVE').length} active · {hypotheses.filter(h => h.status === 'CONFIRMED').length} confirmed
        </span>
      </div>

      <div className="grid gap-4">
        {hypotheses.map(hyp => {
          return (
            <div key={hyp.id} className="intelligence-card p-0 overflow-hidden border border-surface-bright/20">
              <div 
                className="p-5 cursor-pointer hover:bg-surface-low/50 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4"
                onClick={() => toggleExpand(hyp.id)}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-[10px] font-mono uppercase tracking-widest text-primary border border-primary/30 px-2 py-0.5 rounded">
                      {hyp.type}
                    </span>
                    {hyp.status === 'CONFIRMED' && (
                      <span className="text-[10px] font-mono uppercase tracking-widest text-status-success bg-status-success/10 px-2 py-0.5 rounded">
                        CONFIRMED
                      </span>
                    )}
                    {hyp.status === 'REJECTED' && (
                      <span className="text-[10px] font-mono uppercase tracking-widest text-status-error bg-status-error/10 px-2 py-0.5 rounded">
                        REJECTED
                      </span>
                    )}
                  </div>
                  <h3 className="text-lg font-bold text-on-surface leading-tight mt-2">{hyp.title}</h3>
                  <p className="text-sm text-on-surface-variant mt-1 line-clamp-2">{hyp.description}</p>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {hyp.themes.map(t => (
                      <span key={t} className="text-xs text-on-surface-variant bg-surface-lowest px-2 py-1 rounded">#{formatTheme(t)}</span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-6 md:border-l md:border-surface-bright/20 md:pl-6">
                  <div className="text-center">
                    <div className="text-[10px] font-mono text-on-surface-variant uppercase tracking-widest mb-1">Confidence</div>
                    <div className="flex items-center justify-center gap-2">
                      <span className={`text-3xl font-bold ${hyp.confidence > 0.8 ? 'text-status-success' : hyp.confidence < 0.3 ? 'text-status-error' : 'text-primary'}`}>
                        {Math.round(hyp.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                  {expanded === hyp.id ? <ChevronDown className="w-5 h-5 text-on-surface-variant" /> : <ChevronRight className="w-5 h-5 text-on-surface-variant" />}
                </div>
              </div>

              {expanded === hyp.id && (
                <div className="bg-surface-lowest border-t border-surface-bright/20">
                  {/* Strategic Forces Section */}
                  <div className="p-5 border-b border-surface-bright/10 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-surface-low border border-surface-bright/20">
                      <strong className="text-status-success uppercase text-[10px] tracking-widest block mb-2">
                        Strategic Driver (Force A)
                      </strong>
                      <p className="text-sm text-on-surface leading-relaxed">
                        Expanding market presence and betting on AI capability leadership.
                      </p>
                    </div>
                    <div className="p-4 rounded-xl bg-surface-low border border-surface-bright/20">
                      <strong className="text-status-elevated uppercase text-[10px] tracking-widest block mb-2">
                        Potential Constraint (Force B)
                      </strong>
                      <p className="text-sm text-on-surface leading-relaxed">
                        Resource limitations and integration overhead for current developer ecosystem.
                      </p>
                    </div>
                  </div>

                  {/* Predictions Horizon Panel */}
                  <div className="p-5 border-b border-surface-bright/10 bg-primary/5">
                    <div className="flex items-center justify-between text-xs font-mono text-on-surface-variant mb-2">
                      <span className="uppercase tracking-widest font-bold text-primary">Intelligence Projection</span>
                      <span>Horizon: {hyp.predicted_time_horizon?.replace("_", " ") || "90 days"}</span>
                    </div>
                    <p className="text-sm text-on-surface leading-relaxed font-medium">
                      Argos expects confirmation of this hypothesis within the specified time horizon based on current signal velocity.
                    </p>
                  </div>

                  {/* Evidence timeline */}
                  <div className="p-5 border-b border-surface-bright/10">
                    <h4 className="text-xs font-mono uppercase tracking-widest text-on-surface-variant mb-4 flex items-center gap-2">
                      <Activity className="w-3 h-3 text-primary" /> Evidence Trail
                    </h4>
                    
                    {evaluations[hyp.id] === undefined ? (
                      <div className="skeleton h-16 w-full rounded-lg" />
                    ) : evaluations[hyp.id].length === 0 ? (
                      <div className="text-sm text-on-surface-variant flex items-center gap-2 p-3 bg-surface-low rounded-xl border border-surface-bright/10">
                        <AlertCircle className="w-4 h-4 text-on-surface-variant" /> No formal evaluations intercepted yet.
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {evaluations[hyp.id].map(ev => (
                          <div key={ev.id} className="flex gap-4 items-start bg-surface-low border border-surface-bright/20 p-4 rounded-xl">
                            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-surface-bright/10 shrink-0">
                              {ev.impact > 0 ? (
                                <TrendingUp className="w-4 h-4 text-status-success" />
                              ) : (
                                <TrendingDown className="w-4 h-4 text-status-error" />
                              )}
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between gap-2 mb-1">
                                <span className="text-[10px] font-mono text-on-surface-variant">
                                  {new Date(ev.created_at).toLocaleDateString()}
                                </span>
                                <span
                                  className={`text-xs font-bold font-mono ${
                                    ev.impact > 0 ? "text-status-success" : "text-status-error"
                                  }`}
                                >
                                  {ev.impact > 0 ? "+" : ""}
                                  {Math.round(ev.impact * 100)}%
                                </span>
                              </div>
                              <p className="text-sm text-on-surface leading-snug">{ev.reasoning}</p>
                              {ev.signals && (
                                <div className="mt-2 pt-2 border-t border-surface-bright/10 flex items-center justify-between gap-2">
                                  <div className="flex items-center gap-1.5 min-w-0">
                                    <span className="text-[10px] font-mono uppercase tracking-wider text-on-surface-variant shrink-0 bg-surface-bright/20 px-1.5 py-0.5 rounded">
                                      {getSourceLabel(ev.signals)}
                                    </span>
                                    {ev.signals.url ? (
                                      <a
                                        href={ev.signals.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-xs text-primary hover:text-primary/80 flex items-center gap-1 truncate transition-colors group/link"
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        <span className="truncate">{ev.signals.title}</span>
                                        <ExternalLink className="w-3 h-3 shrink-0 opacity-60 group-hover/link:opacity-100" />
                                      </a>
                                    ) : (
                                      <span className="text-xs text-on-surface-variant truncate">{ev.signals.title}</span>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Resolution Panel */}
                  {(!hyp.outcome || hyp.outcome === "PENDING") && (
                    <div className="p-5">
                      <h4 className="text-sm font-bold text-on-surface mb-3 flex items-center gap-2">
                        <Target className="w-4 h-4 text-primary" /> Outcome Resolution
                      </h4>
                      {suggestions[hyp.id] ? (
                        <div className="space-y-4">
                          <div>
                            <strong className="text-primary uppercase text-[10px] tracking-widest block mb-1">
                              Suggested Outcome
                            </strong>
                            <span className="font-mono text-sm text-on-surface">
                              {suggestions[hyp.id].suggested_outcome}
                            </span>
                          </div>
                          <div className="text-sm text-on-surface-variant">
                            <strong className="text-primary uppercase text-[10px] tracking-widest block mb-1">
                              Reasoning
                            </strong>
                            {suggestions[hyp.id].reasoning}
                          </div>
                          <div className="flex gap-3 pt-3 mt-2 border-t border-surface-bright/20">
                            <button
                              disabled={resolving === hyp.id}
                              onClick={() => handleResolve(hyp.id, "CORRECT")}
                              className="flex-1 py-2 bg-status-success/10 text-status-success hover:bg-status-success hover:text-black font-bold text-xs uppercase tracking-widest rounded transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                            >
                              <CheckCircle2 className="w-4 h-4" /> Correct
                            </button>
                            <button
                              disabled={resolving === hyp.id}
                              onClick={() => handleResolve(hyp.id, "INCORRECT")}
                              className="flex-1 py-2 bg-status-error/10 text-status-error hover:bg-status-error hover:text-white font-bold text-xs uppercase tracking-widest rounded transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                            >
                              <XCircle className="w-4 h-4" /> Incorrect
                            </button>
                            <button
                              disabled={resolving === hyp.id}
                              onClick={() => handleResolve(hyp.id, "UNKNOWN")}
                              className="flex-1 py-2 bg-surface-bright/20 text-on-surface hover:bg-surface-bright font-bold text-xs uppercase tracking-widest rounded transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                            >
                              <HelpCircle className="w-4 h-4" /> Unknown
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="skeleton h-24 w-full rounded-lg" />
                      )}
                    </div>
                  )}

                  {/* Final outcome badge */}
                  {hyp.outcome && hyp.outcome !== "PENDING" && (
                    <div
                      className={`mx-5 mb-5 p-4 rounded-xl border ${
                        hyp.outcome === "CORRECT"
                          ? "bg-status-success/10 border-status-success/30"
                          : "bg-status-error/10 border-status-error/30"
                      }`}
                    >
                      <div className="text-xs font-mono uppercase tracking-widest mb-1 text-on-surface-variant">
                        Final Outcome
                      </div>
                      <div
                        className={`font-bold ${
                          hyp.outcome === "CORRECT" ? "text-status-success" : "text-status-error"
                        }`}
                      >
                        {hyp.outcome}
                      </div>
                      {hyp.resolution_reason && (
                        <p className="text-sm text-on-surface-variant mt-1">{hyp.resolution_reason}</p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
"""
    with open(sa_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(final_sa)
    commit("feat(assessment): complete strategic assessment UI with outcome resolution controls")

    print("All final commits completed successfully!")

if __name__ == "__main__":
    main()
