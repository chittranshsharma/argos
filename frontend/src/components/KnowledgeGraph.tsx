"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";
import type { GraphData } from "@/lib/types";

// Dynamic import with SSR disabled for canvas-based rendering
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-argos-accent/30 border-t-argos-accent" />
    </div>
  ),
});

// ── Node Color Map ─────────────────────────────────────────

const TYPE_COLORS: Record<string, string> = {
  Company: "#3b82f6",
  Person: "#22c55e",
  Technology: "#8b5cf6",
  Product: "#eab308",
  Competitor: "#ef4444",
  Entity: "#6b7280",
};

// ── Component ──────────────────────────────────────────────

interface KnowledgeGraphProps {
  data: GraphData;
  width?: number;
  height?: number;
}

export default function KnowledgeGraph({
  data,
  width = 400,
  height = 300,
}: KnowledgeGraphProps) {