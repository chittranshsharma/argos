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
      links: [
        { source: "Anthropic", target: "AWS" },
        { source: "Anthropic", target: "Google" },
        { source: "Anthropic", target: "Jan Leike" },
        { source: "Anthropic", target: "Mike Matas" },
        { source: "Anthropic", target: "Series C" },
        { source: "Anthropic", target: "Claude 3.5" },
        { source: "Jan Leike", target: "Claude 3.5" },
        { source: "OpenAI", target: "Microsoft" },
        { source: "OpenAI", target: "Jan Leike" },
        { source: "Anthropic", target: "OpenAI" }, 
      ]
    };
  }, []);

  useEffect(() => {
    if (mockGraphData.nodes.length > 0) {
      setSelectedNode(mockGraphData.nodes[0]);
    }
  }, [mockGraphData]);

  const drawNode = useCallback((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = node.id;
    const fontSize = 12 / globalScale;
    ctx.font = `${fontSize}px "JetBrains Mono", monospace`;
    
    // Node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, node.val * 0.4, 0, 2 * Math.PI, false);
    ctx.fillStyle = node.color;
    ctx.fill();
    
    // Highlight if selected
    if (selectedNode && selectedNode.id === node.id) {
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.val * 0.4 + 2, 0, 2 * Math.PI, false);
      ctx.strokeStyle = "#f59e0b";
      ctx.lineWidth = 2 / globalScale;
      ctx.stroke();
    }

    // Node label
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = 'rgba(231, 224, 216, 0.9)'; // on-surface
    ctx.fillText(label, node.x, node.y + node.val * 0.4 + fontSize + 2);
  }, [selectedNode]);

  return (
    <div className="w-full relative py-24 bg-surface-lowest">
      
      <div className="max-w-7xl mx-auto px-6 mb-12 relative z-20">
        <h2 className="text-3xl font-bold tracking-tighter uppercase mb-4">Global Knowledge Graph</h2>
        <p className="text-on-surface-variant font-mono text-sm max-w-2xl">
          Entity resolution maps hidden relationships between companies, executives, and capital.
          <br/>
          <span className="text-primary opacity-80 text-xs mt-2 inline-block">Interactive: Click nodes to inspect.</span>
        </p>
      </div>

      <div className="relative w-full h-[600px] border-y border-surface-bright/30 bg-surface-low overflow-hidden" ref={containerRef}>
        {/* Render the graph only on the client */}
        {isClient && (
          <div className="absolute inset-0 opacity-80 cursor-crosshair">
            <ForceGraph2D
              width={dimensions.width}
              height={dimensions.height}
              graphData={mockGraphData}
              nodeLabel={() => ""} // Disable default label, we draw it
              nodeCanvasObject={drawNode}
              onNodeClick={(node) => setSelectedNode(node)}
              linkColor={() => "rgba(168, 162, 158, 0.2)"}
              linkWidth={1.5}
              backgroundColor="transparent"
              d3AlphaDecay={0.02}
              d3VelocityDecay={0.3}
              enableZoomInteraction={false}
              enablePanInteraction={false}
            />
          </div>
        )}

        {/* Cinematic Overlay - Selected Node Panel */}
        {selectedNode && (
          <div className="absolute top-8 left-8 w-72 bg-surface-lowest/90 backdrop-blur-md border border-primary/30 p-5 rounded-lg shadow-[0_0_30px_rgba(0,0,0,0.8)] z-10 animate-fade-in pointer-events-none">
            <div className="flex items-center gap-2 mb-4 text-xs font-mono text-primary uppercase tracking-widest border-b border-primary/20 pb-2">
              <Network className="w-4 h-4" />
              Selected Node
            </div>
            
            <h3 className="text-2xl font-bold text-on-surface mb-6 truncate">{selectedNode.id}</h3>

            <div className="space-y-4 font-mono text-sm">
              <div className="flex justify-between border-b border-surface-bright/20 pb-2">
                <span className="text-on-surface-variant">Activity Level</span>
                <span className={`font-bold ${
                  selectedNode.activityLevel === 'High' ? 'text-status-elevated' : 
                  selectedNode.activityLevel === 'Elevated' ? 'text-status-moderate' :
                  selectedNode.activityLevel === 'Moderate' ? 'text-status-moderate' : 'text-on-surface'
                }`}>{selectedNode.activityLevel}</span>
              </div>
              <div className="flex justify-between border-b border-surface-bright/20 pb-2">
                <span className="text-on-surface-variant">Connections</span>
                <span className="text-on-surface font-bold">{selectedNode.connections}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Momentum</span>
                <span className="text-status-success font-bold">{selectedNode.momentum}</span>
              </div>
            </div>
          </div>
        )}
        
        {/* Scanline Overlay */}
        <div className="absolute inset-0 pointer-events-none" style={{
          backgroundImage: `linear-gradient(rgba(0,0,0,0) 50%, rgba(0,0,0,0.1) 50%)`,
          backgroundSize: '100% 4px',
          zIndex: 5
        }}></div>
      </div>
    </div>
  );
}