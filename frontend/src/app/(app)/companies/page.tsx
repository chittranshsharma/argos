"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getCompanies } from "@/lib/api";
import type { Company } from "@/lib/types";
import { useRouter } from "next/navigation";
import { Search, Plus, Activity, ExternalLink, Globe, FileText, RefreshCw } from "lucide-react";

export default function CompaniesPage() {
  const router = useRouter();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const data = await getCompanies();
        setCompanies(data);
      } catch (err) {
        console.error("Failed to load companies", err);
      } finally {
        setLoading(false);
      }
    }
    load();
    
    // Pick up search query from URL if present
    if (typeof window !== "undefined") {
      const q = new URLSearchParams(window.location.search).get("q");
      if (q) setSearch(q);
    }
  }, []);

  const filtered = companies.filter(c => c.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-on-surface">Companies</h1>
            {!loading && (
              <span className="px-2.5 py-0.5 rounded-full bg-surface-bright/20 border border-surface-bright/30 text-xs font-mono text-on-surface-variant">
                {companies.length} Tracked
              </span>
            )}