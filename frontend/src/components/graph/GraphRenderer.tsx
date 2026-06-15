"use client";

import { useEffect, useRef, useState } from "react";

export interface GraphNode {
  id: string;
  label: string;
  type: "company" | "competitor" | "executive" | "funding" | "launch" | "concept" | "event";
  val: number; // size
  group?: number;
}

export interface GraphLink {
  source: string;
  target: string;
  label?: string;
  type: "competition" | "hiring" | "funding" | "launch" | "partnership" | "acquisition" | "related";
  strength?: "weak" | "medium" | "strong";
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface GraphRendererProps {
  data: GraphData;
  onNodeClick?: (node: GraphNode) => void;
  controlRef?: React.MutableRefObject<any>;
}

// Abstraction layer over react-force-graph-2d
export default function GraphRenderer({ data, onNodeClick, controlRef }: GraphRendererProps) {
  // We use dynamic import for the force graph since it requires browser APIs
  const [ForceGraph2D, setForceGraph2D] = useState<React.ElementType | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const fgRef = useRef<any>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    import("react-force-graph-2d").then((mod) => {
      setForceGraph2D(() => mod.default);
    });
  }, []);

  useEffect(() => {
    if (fgRef.current && ForceGraph2D) {
      // Increase node repulsion to prevent label overlapping
      fgRef.current.d3Force('charge').strength(-450);
      // Ensure links pull nodes together reasonably so they don't float away
      fgRef.current.d3Force('link').distance(60);
      // Center the graph gently to avoid nodes wandering too far off
      fgRef.current.d3Force('center').strength(0.05);
