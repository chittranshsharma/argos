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