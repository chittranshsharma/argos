"use client";

import { useEffect, useState } from "react";
import { getSignalFeed } from "@/lib/api";
import type { Signal } from "@/lib/types";
import SignalFeed from "@/components/SignalFeed";
import { Activity, Filter } from "lucide-react";

export default function IntelligencePage() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>("ALL");
  const [filterCompany, setFilterCompany] = useState<string>("ALL");

  useEffect(() => {
    async function load() {
      try {
        const data = await getSignalFeed({ limit: 100 });
        setSignals(data);
      } catch (err) {
        console.error("Failed to load global feed", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const companies = Array.from(new Set(signals.map(s => s.company_name).filter(Boolean)));
  const types = Array.from(new Set(signals.map(s => s.signal_type || "UNKNOWN")));

  const filteredSignals = signals.filter(s => {
    const sType = s.signal_type || "UNKNOWN";
    if (filterType !== "ALL" && sType !== filterType) return false;
    if (filterCompany !== "ALL" && s.company_name !== filterCompany) return false;
    return true;
  });

  const criticalSignals = filteredSignals.filter(s => s.importance === "high" && (s.score || 0) > 0.85);
  const regularSignals = filteredSignals.filter(s => !(s.importance === "high" && (s.score || 0) > 0.85));

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-on-surface flex items-center gap-3">
            <Activity className="w-8 h-8 text-primary" /> Intelligence Stream
          </h1>
          <p className="text-sm text-on-surface-variant mt-2">
            Real-time feed of all intercepted market signals.
          </p>
        </div>
        
        <div className="flex flex-wrap items-center gap-2">
          <select 
            className="bg-surface-lowest border border-surface-bright/50 rounded-lg px-3 py-1.5 text-sm text-on-surface focus:outline-none focus:border-primary/50"
            value={filterCompany}
            onChange={e => setFilterCompany(e.target.value)}
          >
            <option value="ALL">All Companies</option>
            {companies.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          
          <select 
            className="bg-surface-lowest border border-surface-bright/50 rounded-lg px-3 py-1.5 text-sm text-on-surface focus:outline-none focus:border-primary/50"
            value={filterType}
            onChange={e => setFilterType(e.target.value)}
          >
            <option value="ALL">All Event Types</option>
            {types.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ').toUpperCase()}</option>)}
          </select>