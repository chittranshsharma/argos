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