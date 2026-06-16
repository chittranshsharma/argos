"use client";

import type { ActivityItem, Signal, Hypothesis, HypothesisEvaluation } from "@/lib/types";
import { AlertTriangle, Activity, CheckCircle2, Info, Zap, Target } from "lucide-react";

// ── Severity Hierarchy ────────────────────────────────────

const SEVERITY_STYLES: Record<string, { bg: string; text: string; border: string; icon: React.ElementType; label: string }> = {
  hypothesis: { bg: "bg-purple-500/20", text: "text-purple-400", border: "border-purple-500/40", icon: Zap, label: "STRATEGIC HYPOTHESIS" },
  critical: { bg: "bg-status-critical/10", text: "text-status-critical", border: "border-status-critical/30", icon: AlertTriangle, label: "CRITICAL IMPACT" },
  high: { bg: "bg-primary/10", text: "text-primary", border: "border-primary/30", icon: Activity, label: "HIGH IMPACT" },
  medium: { bg: "bg-status-elevated/10", text: "text-status-elevated", border: "border-status-elevated/30", icon: CheckCircle2, label: "MEDIUM IMPACT" },
  low: { bg: "bg-surface-bright/20", text: "text-on-surface-variant", border: "border-surface-bright/30", icon: Info, label: "LOW IMPACT" },
  evaluation: { bg: "bg-blue-500/20", text: "text-blue-400", border: "border-blue-500/40", icon: Target, label: "EVIDENCE EVALUATED" }
};

// Map old "importance" to new severity
function mapImportanceToSeverity(importance: string) {
  if (importance === "high") return "high"; // Or critical if score is very high
  if (importance === "medium") return "medium";
  return "low";
}

// ── Time Ago Helper ────────────────────────────────────────

function timeAgo(dateStr: string): string {
  if (!dateStr) return "Unknown";
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
function getProviderName(signal: any): string {
  if (signal.url) {
    try {
      const url = new URL(signal.url);
      let host = url.hostname.replace(/^www\./, '');
      if (host.includes('.')) {
        host = host.split('.')[0];
      }
      return host.charAt(0).toUpperCase() + host.slice(1);
    } catch (e) {
      // Invalid URL
    }
  }
  return signal.source || "System";
}

// Generate deterministic AI insight
function getMockInsight(signal: any, finalSeverityKey: string): string {
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
  signals: ActivityItem[];
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
        <p className="text-sm">No intelligence activity detected</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {signals.map((item) => {
        let finalSeverityKey = "low";
        let displayTitle = "";
        let displayContent = "";
        let confidence = 0;
        let signalTypeDisplay = "";

        if (item.activity_type === "hypothesis") {
          finalSeverityKey = "hypothesis";
          displayTitle = item.title;
          displayContent = item.description;
          confidence = Math.round((item.confidence || 0) * 100);
          signalTypeDisplay = "FORECAST";
        } else if (item.activity_type === "evaluation") {
          finalSeverityKey = "evaluation";
          const ev = item as any;
          displayTitle = ev.signals?.title || "Evidence Evaluated";
          displayContent = ev.reasoning || "";
          confidence = ev.impact ? Math.round(Math.abs(ev.impact) * 100) : 50;
          signalTypeDisplay = "EVALUATION";
        } else {
          // Normal signal
          const sig = item as any;
          const baseSeverity = mapImportanceToSeverity(sig.importance || "low");
          finalSeverityKey = (baseSeverity === "high" && (sig.score || 0) > 0.9) ? "critical" : baseSeverity;
          displayTitle = sig.title;
          displayContent = sig.content;
          confidence = sig.score ? Math.round(sig.score * 100) : (80 + ((sig.id?.length || 0) % 20));
          signalTypeDisplay = (sig.signal_type || "Market Event").replace(/_/g, ' ').toUpperCase();
        }

        const severity = SEVERITY_STYLES[finalSeverityKey] || SEVERITY_STYLES["low"];
        const SeverityIcon = severity.icon;
        
        // Emphasize Hypotheses
        const isHypothesis = finalSeverityKey === "hypothesis";
        const isEvaluation = finalSeverityKey === "evaluation";

        return (
          <div
            key={item.id}
            className={`intelligence-card p-5 group flex flex-col gap-3 relative overflow-hidden ${isHypothesis ? 'ring-2 ring-purple-500/50 shadow-[0_0_15px_rgba(168,85,247,0.1)]' : ''} ${isEvaluation ? 'ring-1 ring-blue-500/30' : ''}`}
          >
            {/* Left Accent Line based on Severity */}
            <div className={`absolute left-0 top-0 bottom-0 ${isHypothesis ? 'w-2' : 'w-1'} ${severity.bg} opacity-80`} />

            {/* Header: Meta tags */}
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[10px] font-mono text-on-surface-variant uppercase tracking-widest border border-surface-bright/30 bg-surface-lowest px-2 py-0.5 rounded">
                  {signalTypeDisplay}
                </span>
                <span className={`text-[10px] font-mono uppercase tracking-widest border px-2 py-0.5 rounded flex items-center gap-1 ${severity.bg} ${severity.text} ${severity.border}`}>
                  <SeverityIcon className="w-3 h-3" />
                  {severity.label}
                </span>
              </div>
              <span className="text-xs font-mono text-on-surface-variant">
                {timeAgo(item.timestamp)}
              </span>
            </div>

            {/* Main Content */}
            <div>
              {showCompany && (
                <div className="text-xs font-mono font-bold text-on-surface-variant mb-1 tracking-widest uppercase">
                  [{(item as any).company_name || "Unknown Entity"}]
                </div>
              )}
              <h4 className="text-base font-medium text-on-surface leading-snug group-hover:text-primary transition-colors">
                {(item as any).url ? (
                  <a href={(item as any).url} target="_blank" rel="noopener noreferrer">
                    {displayTitle}
                  </a>
                ) : (
                  displayTitle
                )}
              </h4>

              {/* Stripped Analysis/Content */}
              {!compact && displayContent && (
                <p className={`mt-1.5 text-sm text-on-surface-variant leading-relaxed ${isHypothesis ? '' : 'line-clamp-2'}`}>
                  {stripHtml(displayContent)}
                </p>
              )}

              {/* AI Insight for Raw Signals */}
              {item.activity_type === "signal" && (
                <div className="mt-3 bg-primary/5 border border-primary/10 rounded-md p-2 flex items-start gap-2">
                  <span className="text-[10px] font-bold text-primary uppercase tracking-widest mt-0.5 shrink-0">AI Insight:</span>
                  <span className="text-sm text-on-surface-variant leading-tight">
                    {getMockInsight(item, finalSeverityKey)}
                  </span>
                </div>
              )}
            </div>

            {/* Footer Metrics */}
            <div className="flex items-center justify-between pt-3 border-t border-surface-bright/20 mt-1">
              <div className="flex items-center gap-3">
                {item.activity_type === "hypothesis" && (
                  <span className="text-xs font-mono text-purple-400">
                    Status: <span className="font-bold">{(item as any).status || "ACTIVE"}</span>
                  </span>
                )}
                {item.activity_type === "signal" && (
                  <span className="text-xs font-mono text-on-surface-variant">
                    Source: <span className="text-on-surface capitalize">{getProviderName(item)}</span>
                  </span>
                )}
                {item.activity_type === "evaluation" && (
                  <span className="text-xs font-mono text-blue-400">
                    Impact: <span className="font-bold">{((item as any).impact || 0) > 0 ? "+" : ""}{((item as any).impact || 0)}</span>
                  </span>
                )}
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-16 h-1.5 bg-surface-bright/30 rounded-full overflow-hidden">
                  <div className={`h-full ${severity.bg.replace('/10', '').replace('/20', '')}`} style={{ width: `${confidence}%` }} />
                </div>
                <span className="text-xs font-mono text-on-surface-variant">
                  Conf: {confidence}%
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}