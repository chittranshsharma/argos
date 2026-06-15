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