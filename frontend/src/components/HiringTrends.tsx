"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { HiringTrend } from "@/lib/types";

// ── Trend Colors ───────────────────────────────────────────

const TREND_COLORS: Record<string, string> = {
  growing: "#22c55e",
  stable: "#3b82f6",
  declining: "#ef4444",
};

// ── Custom Tooltip ─────────────────────────────────────────

interface TooltipPayload {
  role: string;
  count: number;
  trend: string;
}

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: TooltipPayload }[];
}) {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload;
  return (
    <div className="rounded-lg bg-argos-surface-2 border border-argos-border px-3 py-2 shadow-xl">
      <p className="text-sm font-medium text-argos-text">{data.role}</p>
      <p className="text-xs text-argos-text-dim">
        Count: <span className="text-argos-text font-medium">{data.count}</span>
      </p>
      <p className="text-xs text-argos-text-dim">
        Trend:{" "}
        <span
          style={{ color: TREND_COLORS[data.trend] || "#6b7280" }}
          className="font-medium capitalize"
        >
          {data.trend}
        </span>
      </p>
    </div>
  );
}

// ── Component ──────────────────────────────────────────────

interface HiringTrendsProps {
  trends: HiringTrend[];
}

export default function HiringTrends({ trends }: HiringTrendsProps) {
  if (!trends || trends.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-argos-text-dim">
        <div className="text-3xl mb-2 opacity-30">▣</div>