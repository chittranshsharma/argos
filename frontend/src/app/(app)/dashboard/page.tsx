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