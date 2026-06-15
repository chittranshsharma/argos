"use client";

import type { Signal } from "@/lib/types";
import { AlertTriangle, Activity, CheckCircle2, Info } from "lucide-react";

// ── Severity Hierarchy ────────────────────────────────────

const SEVERITY_STYLES: Record<string, { bg: string; text: string; border: string; icon: React.ElementType; label: string }> = {
  critical: { bg: "bg-status-critical/10", text: "text-status-critical", border: "border-status-critical/30", icon: AlertTriangle, label: "CRITICAL IMPACT" },
  high: { bg: "bg-primary/10", text: "text-primary", border: "border-primary/30", icon: Activity, label: "HIGH IMPACT" },
  medium: { bg: "bg-status-elevated/10", text: "text-status-elevated", border: "border-status-elevated/30", icon: CheckCircle2, label: "MEDIUM IMPACT" },
  low: { bg: "bg-surface-bright/20", text: "text-on-surface-variant", border: "border-surface-bright/30", icon: Info, label: "LOW IMPACT" },
};

// Map old "importance" to new severity
function mapImportanceToSeverity(importance: string) {
  if (importance === "high") return "high"; // Or critical if score is very high
  if (importance === "medium") return "medium";
  return "low";
}

// ── Time Ago Helper ────────────────────────────────────────

function timeAgo(dateStr: string): string {
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

// Strip HTML tags from content
function stripHtml(html: string): string {
  if (!html) return "";
  return html.replace(/<[^>]*>?/gm, '').replace(/&nbsp;/g, ' ');
}

// Extract provider from URL or fallback to source
function getProviderName(signal: Signal): string {
  if (signal.url) {
    try {
      const url = new URL(signal.url);