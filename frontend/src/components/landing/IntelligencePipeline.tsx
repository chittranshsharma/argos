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
          {steps.map((step, idx) => (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className={`flex flex-col md:flex-row items-start md:items-center gap-6 ${idx % 2 === 0 ? 'md:flex-row-reverse text-left md:text-right' : 'text-left'}`}
            >
              <div className="hidden md:block w-1/2" />
              
              <div className="flex-shrink-0 w-14 h-14 rounded-full bg-surface-low border-2 border-primary/40 flex items-center justify-center relative z-10 shadow-[0_0_15px_rgba(245,158,11,0.1)]">
                {idx < steps.length - 1 ? (
                  <ArrowDown className="w-5 h-5 text-primary" />
                ) : (
                  <div className="w-3 h-3 rounded-full bg-primary animate-pulse" />
                )}
              </div>

              <div className={`md:w-1/2 bg-surface-low/50 backdrop-blur-sm border border-surface-bright/20 p-5 rounded-lg ${idx % 2 === 0 ? 'md:mr-8' : 'md:ml-8'}`}>
                <h4 className="font-mono font-bold text-primary mb-1 uppercase tracking-wider">{step.title}</h4>
                <p className="text-sm text-on-surface-variant font-mono">{step.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}