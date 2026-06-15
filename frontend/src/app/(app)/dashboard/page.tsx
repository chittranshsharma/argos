"use client";

import { useEffect, useState } from "react";
import { getStats, getSignalFeed, getShareOfVoice, getGlobalAnomalies } from "@/lib/api";
import type { DashboardStats, Signal, ShareOfVoiceEntry, Alert } from "@/lib/types";
import SignalFeed from "@/components/SignalFeed";
import { Activity, Zap, FileText, Globe } from "lucide-react";

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
  const [signals, setSignals] = useState<Signal[]>([]);
  const [trending, setTrending] = useState<ShareOfVoiceEntry[]>([]);
  const [anomalies, setAnomalies] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsData, signalsData, trendingData, anomaliesData] = await Promise.all([
          getStats(),
          getSignalFeed({ limit: 20 }),
          getShareOfVoice(7), // past week
          getGlobalAnomalies(7) // past week
        ]);
        setStats(statsData);
        setSignals(signalsData);
        setTrending(trendingData.slice(0, 5));
        setAnomalies(anomaliesData.slice(0, 3));
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