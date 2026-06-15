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
  // Transform data for react-force-graph
  const graphData = useMemo(() => {
    if (!data?.nodes?.length) {
      return { nodes: [], links: [] };
    }

    const nodeMap = new Map<string, boolean>();
    const nodes = data.nodes
      .filter((n) => {
        if (nodeMap.has(n.name)) return false;
        nodeMap.set(n.name, true);
        return true;
      })
      .map((n) => ({
        id: n.name,
        name: n.name,
        type: n.type,
        description: n.description,
        color: TYPE_COLORS[n.type] || TYPE_COLORS.Entity,
      }));

    const nodeNames = new Set(nodes.map((n) => n.id));

    const links = data.links
      .filter((l) => l.source && l.target && nodeNames.has(l.source) && nodeNames.has(l.target))
      .map((l) => ({
        source: l.source,
        target: l.target,
        relation: l.relation,
      }));

    return { nodes, links };
  }, [data]);

  if (!graphData.nodes.length) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-argos-text-dim py-8">
        <div className="text-3xl mb-2 opacity-30">◎</div>
        <p className="text-xs">Knowledge graph is empty</p>
        <p className="text-[10px] mt-1 opacity-60">
          Entities will appear after analysis
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl overflow-hidden border border-argos-border bg-argos-surface/50">
      {/* Legend */}
      <div className="flex flex-wrap gap-2 px-3 pt-3 pb-1">
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1">
            <span
              className="h-2 w-2 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="text-[10px] text-argos-text-dim">{type}</span>
          </div>
        ))}
      </div>

      {/* Graph */}
      <ForceGraph2D
        graphData={graphData}
        width={width}
        height={height}
        backgroundColor="transparent"
        nodeRelSize={6}
        nodeColor={(node: Record<string, unknown>) => (node.color as string) || "#6b7280"}
        nodeLabel={(node: Record<string, unknown>) =>