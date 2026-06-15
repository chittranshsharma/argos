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

      if (controlRef) {
        controlRef.current = {
          zoomIn: () => {
            const currentZoom = fgRef.current.zoom();
            fgRef.current.zoom(currentZoom * 1.5, 400);
          },
          zoomOut: () => {
            const currentZoom = fgRef.current.zoom();
            fgRef.current.zoom(currentZoom / 1.5, 400);
          },
          resetView: () => {
            fgRef.current.zoomToFit(400, 50);
          }
        };
      }
    }
  }, [ForceGraph2D, data, controlRef]);

  useEffect(() => {
    if (containerRef.current) {
      setDimensions({
        width: containerRef.current.clientWidth,
        height: containerRef.current.clientHeight,
      });
    }
    const handleResize = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight,
        });
      }
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  if (!ForceGraph2D) {
    return <div className="w-full h-full flex items-center justify-center text-on-surface-variant font-mono text-sm">Initializing rendering engine...</div>;
  }

  return (
    <div ref={containerRef} className="absolute inset-0 bg-surface-lowest overflow-hidden">
      <ForceGraph2D
        ref={fgRef}
        width={dimensions.width}
        height={dimensions.height}
        graphData={data}
        nodeLabel="label"
        nodeColor={(node: GraphNode) => {
          switch (node.type) {
            case "company": return "#f59e0b"; // Primary Amber
            case "competitor": return "#ef4444"; // Red
            case "executive": return "#3b82f6"; // Blue
            case "funding": return "#10b981"; // Emerald
            case "launch": return "#8b5cf6"; // Violet
            case "event": return "#f43f5e"; // Rose
            case "concept": return "#a8a29e"; // Slate
            default: return "#78716c";
          }
        }}
        nodeRelSize={6}
        linkColor={(link: GraphLink) => {
          const alpha = link.strength === "strong" ? 0.9 : link.strength === "weak" ? 0.4 : 0.7;
          switch (link.type) {
            case "competition": return `rgba(239, 68, 68, ${alpha})`; // Red
            case "partnership": return `rgba(245, 158, 11, ${alpha})`; // Amber
            case "acquisition": return `rgba(16, 185, 129, ${alpha})`; // Emerald
            case "hiring": return `rgba(59, 130, 246, ${alpha})`; // Blue
            case "funding": return `rgba(16, 185, 129, ${alpha})`; // Emerald
            case "launch": return `rgba(139, 92, 246, ${alpha})`; // Violet
            default: return `rgba(168, 162, 158, ${alpha})`; // Gray
          }
        }}
        linkWidth={(link: GraphLink) => {
          let base = link.type === "competition" || link.type === "acquisition" ? 2 : 1;
          if (link.strength === "strong") base += 1.5;
          if (link.strength === "weak") base -= 0.5;
          return base;
        }}
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        onNodeClick={(node: unknown) => onNodeClick && onNodeClick(node as GraphNode)}
        backgroundColor="#140d06" // surface-lowest
        // Custom edge rendering for labels
        linkCanvasObjectMode={() => "after"}
        linkCanvasObject={(link: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
          if (!link.label) return;
          const MAX_FONT_SIZE = 4;
          const LABEL_NODE_MARGIN = 6 * 1.5;

          const start = link.source;
          const end = link.target;

          // Ignore unbound links
          if (typeof start !== 'object' || typeof end !== 'object') return;

          // Calculate text position
          const textPos = {
            x: start.x + (end.x - start.x) / 2,
            y: start.y + (end.y - start.y) / 2
          };