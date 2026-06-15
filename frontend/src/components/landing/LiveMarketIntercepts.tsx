"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

type Signal = {
  id: string;
  time: string;
  type: string;
  company: string;
  description: string;
  confidence: number;
  impact: string;
};

const INITIAL_SIGNALS: Signal[] = [
  { id: "1", time: "12:05:01", type: "FUNDING", company: "DefenseTech", description: "Series B detected ($78M)", confidence: 94, impact: "HIGH" },
  { id: "2", time: "12:04:12", type: "EXECUTIVE MOVEMENT", company: "Cohere", description: "Former OpenAI VP joined Cohere", confidence: 99, impact: "STRATEGIC" },
  { id: "3", time: "12:03:47", type: "PARTNERSHIP", company: "Accenture", description: "Accenture x NVIDIA alliance detected", confidence: 88, impact: "MEDIUM" },
  { id: "4", time: "12:03:11", type: "HIRING SURGE", company: "Anthropic", description: "Anthropic opened 24 AI Safety positions", confidence: 92, impact: "HIGH" },
];

const NEW_SIGNALS: Signal[] = [
  { id: "5", time: "12:06:22", type: "PRODUCT LAUNCH", company: "Palantir", description: "AIP for Defense v3.0 released", confidence: 98, impact: "STRATEGIC" },
  { id: "6", time: "12:07:05", type: "HIRING SURGE", company: "Scale AI", description: "Massive RLHF engineering hiring spike", confidence: 85, impact: "HIGH" },
  { id: "7", time: "12:08:14", type: "PARTNERSHIP", company: "Microsoft", description: "Exclusive cloud compute deal signed", confidence: 91, impact: "STRATEGIC" },
  { id: "8", time: "12:09:59", type: "EXECUTIVE MOVEMENT", company: "xAI", description: "Chief Scientist departure detected", confidence: 77, impact: "HIGH" },
];

export function LiveMarketIntercepts() {
  const [signals, setSignals] = useState<Signal[]>(INITIAL_SIGNALS);
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setSignals((prev) => {
        const signalToAdd = { ...NEW_SIGNALS[index], id: Date.now().toString() + Math.random() };
        return [signalToAdd, ...prev].slice(0, 8);
      });
      setIndex((prev) => (prev + 1) % NEW_SIGNALS.length);
    }, 4500);
    return () => clearInterval(timer);
  }, [index]);

  return (
    <div className="w-full max-w-7xl mx-auto px-6 py-24">
      <div className="flex flex-col gap-2 mb-12">
        <h2 className="text-sm font-mono text-primary uppercase tracking-widest flex items-center gap-2">
          <span className="w-2 h-2 bg-primary rounded-full animate-pulse"></span>
          Live Market Intercepts
        </h2>
        <div className="h-px w-full bg-surface-bright/50"></div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        <div className="md:col-span-4 text-on-surface-variant font-mono text-sm leading-relaxed">
          <p className="mb-4">
            Argos intercepts raw data streams globally. 
            Anomalies are structured, verified, and injected into the intelligence network in real-time.
          </p>
          <p>
            No batch processing. No daily digests. 
            Instant tactical awareness.
          </p>
        </div>

        <div className="md:col-span-8 bg-surface-low border border-surface-bright/50 rounded-lg p-4 overflow-hidden h-[400px] relative font-mono text-sm flex flex-col">
          {/* Fading bottom edge */}
          <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-surface-low to-transparent z-10"></div>
          
          <div className="flex-1 overflow-hidden">
            <AnimatePresence initial={false}>
              {signals.map((sig) => (
                <motion.div
                  key={sig.id}
                  initial={{ opacity: 0, y: -20, backgroundColor: "rgba(245, 158, 11, 0.2)" }}
                  animate={{ opacity: 1, y: 0, backgroundColor: "rgba(245, 158, 11, 0)" }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.8, ease: "easeOut" }}
                  className="mb-4 p-3 border-l-2 border-primary/50 bg-surface-lowest/50"
                >
                  <div className="flex justify-between items-center mb-1 text-xs text-on-surface-variant">
                    <span>[{sig.time}]</span>
                    <span className="flex items-center gap-3">
                      <span>CONF: {sig.confidence}%</span>
                      <span className={`px-1.5 rounded ${sig.impact === 'CRITICAL' ? 'bg-status-critical/20 text-status-critical' : 'bg-status-elevated/20 text-status-elevated'}`}>
                        {sig.impact}
                      </span>
                    </span>
                  </div>
                  <div className="text-primary font-bold mb-1 tracking-wider">{sig.type}</div>
                  <div className="text-on-surface">
                    <span className="font-bold">{sig.company}</span> - {sig.description}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}