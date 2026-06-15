"use client";

import { useEffect, useRef, useState, useMemo, useCallback } from "react";
import dynamic from "next/dynamic";
import { Network } from "lucide-react";

// Use dynamic import for ForceGraph2D to avoid SSR issues
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

export function GraphShowcase() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [isClient, setIsClient] = useState(false);
  const [selectedNode, setSelectedNode] = useState<any>(null);

  useEffect(() => {
    setIsClient(true);
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight,
        });
      }
    };

    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  const mockGraphData = useMemo(() => {
    return {
      nodes: [
        { id: "Anthropic", group: "Target", val: 20, color: "#f59e0b", activityLevel: "High", connections: 47, momentum: "+18%" },
        { id: "AWS", group: "Partner", val: 12, color: "#3b82f6", activityLevel: "Baseline", connections: 124, momentum: "+5%" },
        { id: "Google", group: "Partner", val: 12, color: "#3b82f6", activityLevel: "Moderate", connections: 210, momentum: "-2%" },
        { id: "Jan Leike", group: "Exec", val: 8, color: "#10b981", activityLevel: "Elevated", connections: 15, momentum: "N/A" },
        { id: "Mike Matas", group: "Exec", val: 8, color: "#10b981", activityLevel: "Baseline", connections: 8, momentum: "N/A" },
        { id: "Series C", group: "Funding", val: 15, color: "#a855f7", activityLevel: "None", connections: 3, momentum: "Closed" },
        { id: "Claude 3.5", group: "Product", val: 14, color: "#ef4444", activityLevel: "High", connections: 89, momentum: "+42%" },
        { id: "OpenAI", group: "Target", val: 25, color: "#f59e0b", activityLevel: "High", connections: 312, momentum: "+8%" },
        { id: "Microsoft", group: "Partner", val: 18, color: "#3b82f6", activityLevel: "Elevated", connections: 450, momentum: "+2%" },
      ],