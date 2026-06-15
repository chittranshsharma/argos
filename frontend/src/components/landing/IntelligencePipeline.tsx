"use client";

import { motion } from "framer-motion";
import { ArrowDown } from "lucide-react";

export function IntelligencePipeline() {
  const steps = [
    { title: "Sources", desc: "Global monitoring across 8 open-source vectors." },
    { title: "Specialized Agents", desc: "Domain-specific LLM agents parse noisy unstructured data." },
    { title: "Signal Extraction", desc: "Categorization, confidence scoring, and deduplication." },
    { title: "Knowledge Graph", desc: "Entity mapping and relationship generation." },
    { title: "Analytics Engine", desc: "Velocity tracking and anomaly detection algorithms." },
    { title: "Executive Briefing", desc: "Synthesized strategic intelligence report." },
  ];

  return (
    <div className="w-full max-w-4xl mx-auto px-6 py-24">
      <div className="flex flex-col items-center text-center mb-16">
        <h2 className="text-sm font-mono text-primary uppercase tracking-widest mb-4">Architecture</h2>
        <h3 className="text-3xl md:text-5xl font-bold tracking-tighter uppercase">Intelligence Pipeline</h3>
      </div>

      <div className="relative">
        {/* Connecting Line */}
        <div className="absolute left-[27px] md:left-1/2 top-0 bottom-0 w-px bg-surface-bright/50 -translate-x-1/2"></div>
        
        {/* Animated Flow Pulse */}
        <motion.div 
          className="absolute left-[27px] md:left-1/2 top-0 w-[3px] h-32 bg-gradient-to-b from-transparent via-primary to-transparent -translate-x-1/2 z-0"
          animate={{ y: ["0%", "1000%"] }}
          transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
        />

        <div className="space-y-8 relative z-10">