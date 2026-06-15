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