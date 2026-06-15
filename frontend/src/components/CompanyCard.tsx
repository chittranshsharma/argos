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
