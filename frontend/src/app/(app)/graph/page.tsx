"use client";

import { useEffect, useState, useRef } from "react";
import dynamic from "next/dynamic";
import { getCompanies } from "@/lib/api";
import { Network, Info, ZoomIn, ZoomOut, Maximize, Filter, CheckCircle2, ArrowRight, FileText, Activity } from "lucide-react";
import type { GraphData, GraphNode, GraphLink } from "@/components/graph/GraphRenderer";
import Link from "next/link";

// Load dynamically to avoid SSR issues with ForceGraph
const GraphRenderer = dynamic(() => import("@/components/graph/GraphRenderer"), {
  ssr: false,
});

export default function KnowledgeGraphPage() {
  const [data, setData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const graphControlRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleFullscreen = () => {
    if (containerRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        containerRef.current.requestFullscreen();
      }
    }
  };

  useEffect(() => {
    async function loadGraph() {
      try {
        const companies = await getCompanies();
        
        const nodes: GraphNode[] = [];
        const links: GraphLink[] = [];
        
        // Root node
        nodes.push({ id: "argos_root", label: "Global Market", type: "concept", val: 15 });

        // Mocking a rich, organic Neo4j response
        for (let i = 0; i < companies.length; i++) {
          const company = companies[i];
          const seed = company.name.length + i; // deterministic pseudo-random
          
          nodes.push({ id: company.id, label: company.name, type: "company", val: 12 + (seed % 5) });
          links.push({ source: "argos_root", target: company.id, type: "related", strength: "weak" });
          
          if (seed % 2 === 0) {
            const execId = `${company.id}_exec`;
            nodes.push({ id: execId, label: "Exec Team", type: "concept", val: 6 });
            links.push({ source: company.id, target: execId, type: "related", strength: "strong", label: "HAS TEAM" });
            
            if (seed % 3 !== 0) {
              const ceoId = `${company.id}_ceo`;
              nodes.push({ id: ceoId, label: `CEO: ${company.name.split(' ')[0]}`, type: "executive", val: 4 });
              links.push({ source: execId, target: ceoId, type: "related", strength: "medium" });
            }
          }
          
          if (seed % 3 === 0) {
            const launchId = `${company.id}_launch`;
            nodes.push({ id: launchId, label: "AI Product Launch", type: "launch", val: 8 });
            links.push({ source: company.id, target: launchId, type: "launch", strength: "strong", label: "LAUNCHED" });
          }
          
          if (seed % 4 === 0 || seed % 5 === 0) {
            const fundingId = `${company.id}_funding`;
            nodes.push({ id: fundingId, label: "Series D ($100M)", type: "funding", val: 10 });
            links.push({ source: company.id, target: fundingId, type: "funding", strength: "strong", label: "RAISED FUNDING" });
          }

          // Intelligence Events
          if (seed % 5 === 1) {
             const eventId = `${company.id}_event_hire`;
             nodes.push({ id: eventId, label: "Hiring Spike (AI Engineers)", type: "event", val: 7 });
             links.push({ source: company.id, target: eventId, type: "hiring", strength: "medium", label: "DETECTED" });
          }
          if (seed % 7 === 2) {
             const eventId = `${company.id}_event_patent`;
             nodes.push({ id: eventId, label: "Patent Filing: AGI Routing", type: "event", val: 8 });
             links.push({ source: company.id, target: eventId, type: "launch", strength: "strong", label: "FILED" });
          }
          if (seed % 6 === 3) {
             const eventId = `${company.id}_event_acq`;
             nodes.push({ id: eventId, label: "Acquisition Rumor", type: "event", val: 9 });
             links.push({ source: company.id, target: eventId, type: "acquisition", strength: "weak", label: "RUMORED" });
          }

          // Cross company relations
          if (companies.length > 1) {
            for (let j = i + 1; j < companies.length; j++) {
               const other = companies[j];
               const pairSeed = seed + other.name.length;
               
               if (pairSeed % 3 === 0) {
                 links.push({
                   source: company.id,
                   target: other.id,
                   type: "competition",
                   strength: pairSeed % 2 === 0 ? "strong" : "medium",
                   label: "COMPETES WITH"
                 });
               } else if (pairSeed % 5 === 0) {
                 links.push({
                   source: company.id,
                   target: other.id,
                   type: "partnership",
                   strength: "medium",
                   label: "PARTNERS WITH"
                 });
               } else if (pairSeed % 7 === 0) {
                 links.push({
                   source: company.id,
                   target: other.id,
                   type: "hiring",
                   strength: "strong",
                   label: "HIRED FROM"
                 });
               }
            }
          }
        }

        setData({ nodes, links });
      } catch (err) {
        console.error("Failed to build graph topology", err);
      } finally {
        setLoading(false);
      }
    }
    
    loadGraph();
  }, []);

  const getNodeLinkCount = (nodeId: string) => {
    return data.links.filter(l => 
      l.source === nodeId || l.target === nodeId || 
      (l.source as any).id === nodeId || (l.target as any).id === nodeId
    ).length;
  };

  const generateAIAssessment = (node: GraphNode) => {
    // Collect all links connected to this node
    const connectedLinks = data.links.filter(
      l => l.source === node.id || l.target === node.id || (l.source as any).id === node.id || (l.target as any).id === node.id
    );

    if (connectedLinks.length === 0) {
      return `Isolated node detected. Insufficient topological data to generate a high-confidence assessment for ${node.label}.`;
    }

    if (node.type === "company") {
      const hires = connectedLinks.filter(l => l.type === "hiring").length;
      const funding = connectedLinks.filter(l => l.type === "funding").length;
      const competitors = connectedLinks.filter(l => l.type === "competition").length;
      const launches = connectedLinks.filter(l => l.type === "launch").length;

      let assessment = `Strategic analysis of ${node.label} indicates `;
      if (hires > 0 && launches > 0) {
        assessment += `aggressive expansion through targeted talent acquisition and rapid product deployment. `;
      } else if (funding > 0) {
        assessment += `recent capital influx is likely fueling upcoming strategic maneuvers. `;
      } else if (competitors > 1) {
        assessment += `significant competitive pressure from multiple vectors within the sector. `;
      } else {
        assessment += `stable positioning with ongoing tactical developments. `;
      }

      if (competitors > 0) {
        assessment += `Requires active monitoring of competitor overlaps.`;
      }
      return assessment;
    }

    if (node.type === "event") {
      const isCritical = node.label.toLowerCase().includes("patent") || node.label.toLowerCase().includes("acquisition");
      if (isCritical) {
         return `High-impact anomaly detected. This event signals a probable shift in the associated company's long-term strategy and warrants immediate analyst review.`;
      }
      return `Tactical market signal. Indicates elevated activity within the cluster but remains within expected behavioral baselines.`;
    }

    return `Identified as a structural node within its cluster. Vector connectivity suggests it plays a supporting role in broader market movements.`;
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      <div className="flex items-center justify-between mb-6 shrink-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-on-surface flex items-center gap-3">
            <Network className="w-8 h-8 text-primary" /> Entity Matrix
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Topological map of all tracked entities and their relationships.
          </p>
        </div>
      </div>

      <div className="flex-1 flex gap-6 overflow-hidden">
        <div ref={containerRef} className="flex-1 glass-panel rounded-2xl overflow-hidden relative border border-surface-bright/30">
          {loading ? (
            <div className="absolute inset-0 flex items-center justify-center text-on-surface-variant font-mono text-sm">
              <span className="relative flex h-3 w-3 mr-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
                <span className="relative inline-flex h-3 w-3 rounded-full bg-primary" />
              </span>
              Calculating node vectors...
            </div>
          ) : (
            <GraphRenderer 
              data={data} 
              onNodeClick={(node) => setSelectedNode(node)} 
              controlRef={graphControlRef}
            />
          )}
          
          <div className="absolute top-4 left-4 flex gap-2 flex-wrap max-w-md">
            {[
              { label: "Company", color: "bg-[#f59e0b]" },
              { label: "Competitor", color: "bg-[#ef4444]" },
              { label: "Executive", color: "bg-[#3b82f6]" },
              { label: "Funding", color: "bg-[#10b981]" },
              { label: "Launch", color: "bg-[#8b5cf6]" },
              { label: "Intel Event", color: "bg-[#f43f5e]" },
              { label: "Partnership", color: "bg-[#f59e0b]" }
            ].map(type => (
              <div key={type.label} className="px-3 py-1.5 rounded-lg bg-surface-lowest/80 backdrop-blur border border-surface-bright/30 flex items-center gap-2 text-xs font-mono text-on-surface">
                <div className={`w-2 h-2 rounded-full ${type.color}`} /> {type.label}
              </div>
            ))}
          </div>

          <div className="absolute top-4 right-4 flex gap-2">
            <button onClick={() => graphControlRef.current?.zoomIn()} className="p-2 rounded bg-surface-lowest/80 backdrop-blur border border-surface-bright/30 hover:bg-white/5 transition-colors text-on-surface-variant">
              <ZoomIn className="w-4 h-4" />
            </button>