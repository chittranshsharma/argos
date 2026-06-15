"use client";

import type { Company } from "@/lib/types";
import Link from "next/link";

// ── Source Icons ────────────────────────────────────────────

function countActiveSources(company: Company): number {
  let count = 0;
  if (company.github_org) count++;
  if (company.careers_url) count++;
  if (company.reddit_sub) count++;
  if (company.producthunt_slug) count++;
  if (company.linkedin_url) count++;
  if (company.changelog_url) count++;
  if (company.news_keywords?.length) count++;
  count++; // HackerNews is always active
  return count;
}

function timeAgo(dateStr: string | null): string {
  if (!dateStr) return "Never";
  const now = new Date();
  const date = new Date(dateStr);
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

// ── Component ──────────────────────────────────────────────

interface CompanyCardProps {
  company: Company;
  signalCount?: number;
}

export default function CompanyCard({ company, signalCount }: CompanyCardProps) {
  const sources = countActiveSources(company);

  return (
    <Link href={`/companies/${company.id}`}>
      <div className="glass-card p-5 cursor-pointer group h-full">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-argos-accent/20 to-blue-600/10 border border-argos-accent/20 text-argos-accent font-bold text-lg group-hover:from-argos-accent/30 group-hover:to-blue-600/20 transition-all duration-300">
              {company.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h3 className="text-base font-semibold text-argos-text group-hover:text-argos-accent transition-colors">
                {company.name}
              </h3>
              {company.website && (
                <p className="text-xs text-argos-text-dim truncate max-w-[180px]">
                  {company.website.replace(/^https?:\/\//, "")}
                </p>
              )}
            </div>
          </div>

          {/* Active indicator */}
          <span className="relative flex h-2.5 w-2.5 mt-1">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-argos-success opacity-75" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-argos-success" />
          </span>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="rounded-xl bg-argos-surface-2/60 p-2.5 text-center border border-argos-border/50">
            <div className="text-lg font-bold text-argos-accent">{sources}</div>
            <div className="text-[10px] text-argos-text-dim uppercase tracking-wider">Sources</div>
          </div>
          <div className="rounded-xl bg-argos-surface-2/60 p-2.5 text-center border border-argos-border/50">
            <div className="text-lg font-bold text-argos-success">
              {signalCount ?? "—"}
            </div>
            <div className="text-[10px] text-argos-text-dim uppercase tracking-wider">Signals</div>
          </div>
          <div className="rounded-xl bg-argos-surface-2/60 p-2.5 text-center border border-argos-border/50">
            <div className="text-lg font-bold text-argos-text">
              {sources > 0 ? "8" : "0"}
            </div>
            <div className="text-[10px] text-argos-text-dim uppercase tracking-wider">Agents</div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-argos-text-dim">
          <span>Last monitored: {timeAgo(company.last_monitored)}</span>
          <span className="text-argos-accent group-hover:translate-x-1 transition-transform duration-200">
            View →
          </span>
        </div>
      </div>
    </Link>
  );
}