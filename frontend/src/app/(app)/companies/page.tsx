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
          </div>
          <p className="text-sm text-on-surface-variant mt-1">Manage and monitor target companies</p>
        </div>
        <Link 
          href="/companies/new"
          className="flex items-center gap-2 bg-primary text-black font-bold px-4 py-2 rounded-lg hover:scale-[1.02] active:scale-95 transition-transform"
        >
          <Plus className="w-4 h-4" />
          Add Company
        </Link>
      </div>

      <div className="flex gap-4 items-center">
        <div className="relative flex-1 max-w-md">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <Search className="h-4 w-4 text-on-surface-variant" />
          </div>
          <input
            type="text"
            className="w-full bg-surface border border-surface-bright/30 rounded-lg pl-10 pr-4 py-2 text-sm text-on-surface focus:outline-none focus:border-primary/50 transition-all"
            placeholder="Filter entities..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="glass-panel rounded-xl overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr>
              <th className="font-mono text-xs text-on-surface-variant uppercase pb-4 pt-5 px-6 border-b border-surface-bright/20 w-1/3">Company</th>
              <th className="font-mono text-xs text-on-surface-variant uppercase pb-4 pt-5 px-6 border-b border-surface-bright/20">Sources</th>
              <th className="font-mono text-xs text-on-surface-variant uppercase pb-4 pt-5 px-6 border-b border-surface-bright/20 text-center">Activity Score</th>
              <th className="font-mono text-xs text-on-surface-variant uppercase pb-4 pt-5 px-6 border-b border-surface-bright/20">Status</th>
              <th className="font-mono text-xs text-on-surface-variant uppercase pb-4 pt-5 px-6 border-b border-surface-bright/20 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="p-6">
                  <div className="space-y-3">
                    <div className="skeleton h-12 w-full" />
                    <div className="skeleton h-12 w-full" />
                    <div className="skeleton h-12 w-full" />
                  </div>
                </td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-12 text-center text-on-surface-variant">
                  <Globe className="w-12 h-12 mx-auto mb-4 opacity-20" />
                  <p>No companies found matching &quot;{search}&quot;</p>
                </td>
              </tr>
            ) : (
              filtered.map((company) => {
                const activityScore = Math.round(company.intelligence_score || 0);
                
                return (
                  <tr 
                    key={company.id} 
                    onClick={() => router.push(`/companies/${company.id}`)}
                    className="hover:bg-white/5 transition-colors border-b border-surface-bright/10 group cursor-pointer"
                  >
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-lg bg-surface-bright/20 flex items-center justify-center text-on-surface font-bold text-sm">
                          {company.name.charAt(0)}
                        </div>
                        <span className="font-medium text-on-surface group-hover:text-primary transition-colors">{company.name}</span>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex gap-2 text-on-surface-variant">
                        {company.website && <span title="Website"><Globe className="w-4 h-4" /></span>}
                        {company.github_org && <span title="GitHub"><Activity className="w-4 h-4" /></span>}
                        {company.news_keywords?.length > 0 && <span title="News Intel"><FileText className="w-4 h-4" /></span>}
                        {company.linkedin_url && <span title="LinkedIn"><ExternalLink className="w-4 h-4" /></span>}
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex items-center justify-center gap-2">
                        <div className="font-mono text-sm font-bold text-on-surface">{activityScore}</div>
                        <div className="w-16 h-1.5 bg-surface-bright/20 rounded-full overflow-hidden">
                          <div className="h-full bg-primary" style={{ width: `${activityScore}%` }} />
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono bg-status-success/10 text-status-success border border-status-success/20">
                        Active
                      </span>
                    </td>
                    <td className="py-4 px-6 text-right">
                      <button 
                        onClick={async (e) => {
                          e.stopPropagation(); // Prevent row click
                          try {
                            const { triggerMonitoring } = await import("@/lib/api");
                            await triggerMonitoring(company.id);
                            // Set a local state to show it's scanning if we had one, but for now just reload
                            window.location.reload();
                          } catch (err) {
                            console.error("Failed to trigger scan", err);
                          }
                        }}
                        className="inline-flex items-center gap-2 px-3 py-1.5 bg-surface-lowest border border-surface-bright/30 rounded text-xs font-bold text-on-surface hover:text-primary transition-colors"
                      >
                        <RefreshCw className="w-3 h-3" />
                        Scan Now
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}