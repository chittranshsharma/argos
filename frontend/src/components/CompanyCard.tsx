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