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