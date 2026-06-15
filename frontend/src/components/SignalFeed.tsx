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
      let host = url.hostname.replace(/^www\./, '');
      // Capitalize first letter of domain
      if (host.includes('.')) {
        host = host.split('.')[0];
      }
      return host.charAt(0).toUpperCase() + host.slice(1);
    } catch (e) {
      // Invalid URL
    }
  }
  return signal.source;
}

// Generate deterministic AI insight
function getMockInsight(signal: Signal, finalSeverityKey: string): string {
  const type = (signal.signal_type || "").toUpperCase();
  if (finalSeverityKey === "critical") return "Critical anomaly detected. High probability of strategic pivot or major disruption.";
  if (type.includes("HIRE") || type.includes("HIRING") || type.includes("PERSONNEL")) return "Talent acquisition velocity increasing in specialized roles.";
  if (type.includes("FUNDING") || type.includes("CAPITAL")) return "Capital influx suggests impending growth phase or acquisition strategy.";
  if (type.includes("LAUNCH") || type.includes("PRODUCT")) return "Product expansion indicates movement into adjacent market territories.";
  if (finalSeverityKey === "high") return "Elevated activity level. Suggests upcoming strategic announcement.";
  return "Standard market activity. Monitoring for further developments.";
}

// ── Component ──────────────────────────────────────────────

interface SignalFeedProps {
  signals: Signal[];
  showCompany?: boolean;
  compact?: boolean;
}

export default function SignalFeed({
  signals,
  showCompany = true,
  compact = false,
}: SignalFeedProps) {
  if (!signals || signals.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-on-surface-variant">
        <Activity className="w-12 h-12 mb-3 opacity-20" />
        <p className="text-sm">No intelligence signals detected</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {signals.map((signal) => {
        // Derive visual properties
        const severityKey = mapImportanceToSeverity(signal.importance);
        // Elevate to critical if high score
        const finalSeverityKey = (severityKey === "high" && (signal.score || 0) > 0.9) ? "critical" : severityKey;
        const severity = SEVERITY_STYLES[finalSeverityKey];
        const SeverityIcon = severity.icon;

        const confidence = signal.score ? Math.round(signal.score * 100) : (80 + (signal.id.length % 20)); // Fallback for UI density if score missing
        const signalType = (signal.signal_type || "Market Event").replace(/_/g, ' ').toUpperCase();

        return (
          <div
            key={signal.id}
            className={`intelligence-card p-5 group flex flex-col gap-3 relative overflow-hidden`}
          >
            {/* Left Accent Line based on Severity */}
            <div className={`absolute left-0 top-0 bottom-0 w-1 ${severity.bg} opacity-50`} />

            {/* Header: Meta tags */}
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[10px] font-mono text-on-surface-variant uppercase tracking-widest border border-surface-bright/30 bg-surface-lowest px-2 py-0.5 rounded">
                  {signalType}
                </span>
                <span className={`text-[10px] font-mono uppercase tracking-widest border px-2 py-0.5 rounded flex items-center gap-1 ${severity.bg} ${severity.text} ${severity.border}`}>
                  <SeverityIcon className="w-3 h-3" />
                  {severity.label}
                </span>
              </div>
              <span className="text-xs font-mono text-on-surface-variant">
                {timeAgo(signal.collected_at)}
              </span>
            </div>

            {/* Main Content */}
            <div>
              {showCompany && (
                <div className="text-xs font-mono font-bold text-on-surface-variant mb-1 tracking-widest uppercase">
                  [{signal.company_name}]
                </div>
              )}