"use client";

import { useEffect, useState } from "react";
import { 
  LineChart, Activity, ShieldAlert, BarChart3,
  Globe, AlertTriangle, Building2, Zap, ArrowUpRight, ArrowDownRight, Minus, Radar
} from "lucide-react";
import { 
  getGlobalKPIs, getGlobalVelocity, getGlobalSentiment, getGlobalAnomalies, getRankings,
  getShareOfVoice, getIntelligenceDistribution
} from "@/lib/api";
import type { 
  GlobalKPIs, VelocityEntry, SentimentEntry, Alert, RankingEntry, ShareOfVoiceEntry, DistributionEntry 
} from "@/lib/types";
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend,
  BarChart, Bar, Cell, PieChart, Pie, Sector
} from "recharts";

export default function AnalyticsPage() {
  const [days, setDays] = useState(30);
  const [kpis, setKpis] = useState<GlobalKPIs | null>(null);
  const [velocity, setVelocity] = useState<VelocityEntry[]>([]);
  const [sentiment, setSentiment] = useState<SentimentEntry[]>([]);
  const [anomalies, setAnomalies] = useState<Alert[]>([]);
  const [rankings, setRankings] = useState<RankingEntry[]>([]);
  const [sov, setSov] = useState<ShareOfVoiceEntry[]>([]);
  const [distribution, setDistribution] = useState<DistributionEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [k, v, s, a, r, so, d] = await Promise.all([
          getGlobalKPIs(days),
          getGlobalVelocity(days),
          getGlobalSentiment(days),
          getGlobalAnomalies(days),
          getRankings(10),
          getShareOfVoice(days),
          getIntelligenceDistribution()
        ]);
        setKpis(k);
        setVelocity(v);
        setSentiment(s);
        setAnomalies(a);
        setRankings(r);
        setSov(so);
        setDistribution(d);
      } catch (err) {
        console.error("Failed to load analytics data", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [days]);

  return (
    <div className="space-y-4 max-w-[1600px] mx-auto pb-12 px-2">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-on-surface flex items-center gap-3 font-mono uppercase">
            <LineChart className="w-6 h-6 text-primary" /> Strategic Market Analytics Engine
          </h1>
        </div>
        <div className="flex gap-1 bg-surface-bright/20 p-1 rounded-md border border-surface-bright/30">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1 text-xs font-mono uppercase font-bold rounded transition-colors ${
                days === d 
                  ? "bg-primary text-black" 
                  : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              {d}D
            </button>
          ))}
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "TRACKED ENTITIES", value: kpis?.tracked_companies || 0, icon: Building2, color: "text-primary" },
          { label: "SIGNALS ANALYZED", value: kpis?.signals_analyzed || 0, icon: Activity, color: "text-status-info" },
          { label: "CRITICAL EVENTS", value: kpis?.critical_events || 0, icon: ShieldAlert, color: "text-status-critical" },
          { label: "MARKET SENTIMENT", value: kpis?.average_sentiment?.toFixed(1) || "7.5", icon: Globe, color: "text-status-success", suffix: "/15" }
        ].map((kpi, i) => (
          <div key={i} className="bg-surface/50 border border-surface-bright/30 p-4 flex items-center justify-between">
            <div>
              <p className="text-[10px] text-on-surface-variant font-mono uppercase tracking-widest">{kpi.label}</p>
              <div className="flex items-baseline gap-1 mt-1">
                <p className="text-2xl font-mono font-bold text-on-surface">
                  {loading ? "-" : kpi.value}
                </p>
                {kpi.suffix && !loading && (
                  <span className="text-xs font-mono text-on-surface-variant">{kpi.suffix}</span>
                )}
              </div>
            </div>
            <kpi.icon className={`w-6 h-6 ${kpi.color} opacity-80`} />
          </div>
        ))}
      </div>

      {/* Top Section: Hero Velocity & Active Radar */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-4">
        <div className="xl:col-span-3 bg-surface/50 border border-surface-bright/30 p-4">
          <div className="flex items-center gap-2 mb-4 border-b border-surface-bright/20 pb-2">
            <BarChart3 className="w-4 h-4 text-primary" />
            <h3 className="text-sm font-mono uppercase font-bold text-on-surface tracking-wider">Signal Velocity Matrix</h3>
          </div>
          <div className="h-[300px] w-full">
            {loading ? (
              <div className="w-full h-full flex items-center justify-center text-on-surface-variant font-mono text-xs">LOADING MATRIX...</div>
            ) : velocity.length === 0 ? (
              <div className="w-full h-full flex items-center justify-center text-on-surface-variant font-mono text-xs">NO SIGNAL DATA</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={velocity} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                  <XAxis dataKey="date" stroke="#666" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(str) => str.split("-").slice(1).join("/")} />
                  <YAxis stroke="#666" fontSize={10} tickLine={false} axisLine={false} />
                  <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
                  <RechartsTooltip 
                    cursor={{fill: '#222'}}
                    contentStyle={{ backgroundColor: '#000', border: '1px solid #333', borderRadius: '0px', fontFamily: 'monospace', fontSize: '12px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                  <Bar dataKey="hiring" fill="#4ade80" name="Hiring" />
                  <Bar dataKey="funding" fill="#fbbf24" name="Funding" />
                  <Bar dataKey="launches" fill="#f472b6" name="Launches" />
                  <Bar dataKey="news" fill="#60a5fa" name="News" />
                  <Bar dataKey="executive" fill="#a78bfa" name="Executive" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="bg-surface/50 border border-surface-bright/30 p-4 flex flex-col">
          <div className="flex items-center gap-2 mb-4 border-b border-surface-bright/20 pb-2">
            <Radar className="w-4 h-4 text-status-info" />
            <h3 className="text-sm font-mono uppercase font-bold text-on-surface tracking-wider">Active Radar</h3>
          </div>
          <div className="flex-1 overflow-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="text-on-surface-variant border-b border-surface-bright/20">
                  <th className="pb-2 font-normal">ENTITY</th>
                  <th className="pb-2 font-normal text-right">SCORE</th>
                  <th className="pb-2 font-normal text-right">MOMENTUM</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={3} className="py-4 text-center text-on-surface-variant">LOADING...</td></tr>
                ) : rankings.slice(0, 8).map((r) => (
                  <tr key={r.id} className="border-b border-surface-bright/10 hover:bg-surface-bright/10 transition-colors">
                    <td className="py-2.5 text-on-surface truncate max-w-[100px]">{r.company}</td>
                    <td className="py-2.5 text-right font-bold text-primary">{r.score.toFixed(1)}</td>
                    <td className={`py-2.5 text-right flex items-center justify-end gap-1 ${r.change > 0 ? "text-status-success" : r.change < 0 ? "text-status-critical" : "text-on-surface-variant"}`}>
                      {r.change === 0 ? (
                        <span className="text-on-surface-variant/50">-</span>
                      ) : (
                        <>
                          {r.change > 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                          {Math.abs(r.change).toFixed(1)}
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Middle Section: Anomalies & Distributions */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
        
        <div className="xl:col-span-2 bg-surface/50 border border-status-critical/30 p-0 flex flex-col">
          <div className="flex items-center gap-2 p-4 border-b border-status-critical/20 bg-status-critical/5">
            <AlertTriangle className="w-4 h-4 text-status-critical" />
            <h3 className="text-sm font-mono uppercase font-bold text-status-critical tracking-wider">Anomaly Correlation Log</h3>
          </div>
          <div className="p-0 overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="text-on-surface-variant border-b border-surface-bright/20 bg-surface-bright/5">
                  <th className="p-3 font-normal">TIMESTAMP</th>
                  <th className="p-3 font-normal">ENTITY</th>
                  <th className="p-3 font-normal">TYPE</th>
                  <th className="p-3 font-normal text-center">CONFIDENCE</th>
                  <th className="p-3 font-normal">IMPACT</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-bright/10">
                {loading ? (
                  <tr><td colSpan={5} className="py-8 text-center text-on-surface-variant">LOADING LOGS...</td></tr>
                ) : anomalies.length === 0 ? (
                  <tr><td colSpan={5} className="py-8 text-center text-on-surface-variant">NO CRITICAL ANOMALIES DETECTED</td></tr>
                ) : anomalies.map((a) => (
                  <tr key={a.id} className="hover:bg-surface-bright/5 transition-colors">
                    <td className="p-3 text-on-surface-variant">{new Date(a.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
                    <td className="p-3 text-on-surface font-bold">{a.company_name}</td>
                    <td className="p-3 text-on-surface">{a.alert_type.toUpperCase()}</td>
                    <td className="p-3 text-center">
                      <span className={`px-2 py-0.5 rounded bg-surface-bright/20 ${a.confidence_score && a.confidence_score > 90 ? 'text-status-success' : 'text-status-info'}`}>
                        {a.confidence_score ? `${a.confidence_score}%` : 'N/A'}
                      </span>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded border ${a.impact_level === 'Critical' ? 'border-status-critical text-status-critical bg-status-critical/10' : 'border-status-info text-status-info bg-status-info/10'}`}>
                        {a.impact_level?.toUpperCase() || 'HIGH'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="xl:col-span-3 grid grid-cols-2 gap-4">
          <div className="bg-surface/50 border border-surface-bright/30 p-4">
            <div className="flex items-center gap-2 mb-4 border-b border-surface-bright/20 pb-2">
              <Zap className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-mono uppercase font-bold text-on-surface tracking-wider">Score Distribution</h3>
            </div>
            <div className="h-[200px] w-full">
              {loading ? (
                <div className="w-full h-full flex items-center justify-center text-on-surface-variant font-mono text-xs">LOADING...</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={distribution} layout="vertical" margin={{ top: 0, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#222" horizontal={true} vertical={false} />
                    <XAxis type="number" stroke="#666" fontSize={10} tickLine={false} axisLine={false} hide />
                    <YAxis type="category" dataKey="range" stroke="#888888" fontSize={10} tickLine={false} axisLine={false} width={50} />
                    <RechartsTooltip 
                      cursor={{fill: '#222'}}
                      contentStyle={{ backgroundColor: '#000', border: '1px solid #333', borderRadius: '0px', fontFamily: 'monospace', fontSize: '12px' }}
                    />
                    <Bar dataKey="count" fill="#4ade80" radius={[0, 2, 2, 0]} barSize={20} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          <div className="bg-surface/50 border border-surface-bright/30 p-4">
            <div className="flex items-center gap-2 mb-4 border-b border-surface-bright/20 pb-2">
              <Activity className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-mono uppercase font-bold text-on-surface tracking-wider">Share of Voice</h3>
            </div>
            <div className="h-[200px] w-full relative flex gap-4">
              {loading ? (
                <div className="w-full h-full flex items-center justify-center text-on-surface-variant font-mono text-xs">LOADING...</div>
              ) : sov.length === 0 ? (
                <div className="w-full h-full flex items-center justify-center text-on-surface-variant font-mono text-xs">NO DATA</div>
              ) : (
                <>
                  <div className="w-1/2 h-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={sov.slice(0, 5)}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          paddingAngle={2}
                          dataKey="volume"
                          nameKey="company"
                          stroke="none"
                          startAngle={90}
                          endAngle={-270}
                        >
                          {sov.slice(0, 5).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={["#4ade80", "#60a5fa", "#a78bfa", "#f472b6", "#fbbf24"][index % 5]} />
                          ))}
                        </Pie>
                        <RechartsTooltip 
                          contentStyle={{ backgroundColor: '#000', border: '1px solid #333', borderRadius: '0px', fontFamily: 'monospace', fontSize: '12px' }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="w-1/2 h-full flex flex-col justify-center gap-3">
                    {sov.slice(0, 5).map((entry, i) => (
                      <div key={entry.company} className="flex flex-col gap-1">
                        <div className="flex justify-between text-xs font-mono">
                          <span className="text-on-surface truncate max-w-[130px]" title={entry.company}>{entry.company}</span>
                          <span className="text-on-surface-variant">{entry.percentage}%</span>
                        </div>
                        <div className="h-1.5 w-full bg-surface-bright/20 rounded-full overflow-hidden">
                          <div 
                            className="h-full rounded-full" 
                            style={{ 
                              width: `${entry.percentage}%`, 
                              backgroundColor: ["#4ade80", "#60a5fa", "#a78bfa", "#f472b6", "#fbbf24"][i % 5] 
                            }} 
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

      </div>

      {/* Bottom Section: Sentiment Heatmap */}
      <div className="bg-surface/50 border border-surface-bright/30 p-4">
        <div className="flex items-center gap-2 mb-4 border-b border-surface-bright/20 pb-2">
          <Globe className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-mono uppercase font-bold text-on-surface tracking-wider">Company Sentiment Heatmap</h3>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2">
          {loading ? (
            <div className="col-span-full py-8 text-center text-on-surface-variant font-mono text-xs">LOADING...</div>
          ) : sentiment.map((s) => {
            const isGood = s.sentiment_score > 10;
            const isBad = s.sentiment_score < 5;
            return (
              <div 
                key={s.company_name} 
                className={`p-3 border flex flex-col justify-between h-[80px] ${
                  isGood ? 'bg-status-success border-status-success' : 
                  isBad ? 'bg-status-critical border-status-critical' : 
                  'bg-status-elevated border-status-elevated'
                }`}
              >
                <div className={`text-xs font-mono font-bold truncate ${isGood || isBad ? 'text-black' : 'text-black'}`} title={s.company_name}>{s.company_name}</div>
                <div className={`text-xl font-mono font-bold ${isGood || isBad ? 'text-black' : 'text-black'}`}>
                  {s.sentiment_score.toFixed(1)}
                </div>
              </div>
            )
          })}
        </div>
      </div>

    </div>
  );
}