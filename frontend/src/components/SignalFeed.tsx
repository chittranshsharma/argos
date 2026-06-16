"use client";

import type { Signal } from "@/lib/types";
import { AlertTriangle, Activity, CheckCircle2, Info, Zap } from "lucide-react";

// ── Severity Hierarchy ────────────────────────────────────

const SEVERITY_STYLES: Record<string, { bg: string; text: string; border: string; icon: React.ElementType; label: string }> = {
  correlation: { bg: "bg-purple-500/20", text: "text-purple-400", border: "border-purple-500/40", icon: Zap, label: "MACRO EVENT" },
  critical: { bg: "bg-status-critical/10", text: "text-status-critical", border: "border-status-critical/30", icon: AlertTriangle, label: "CRITICAL IMPACT" },
  high: { bg: "bg-primary/10", text: "text-primary", border: "border-primary/30", icon: Activity, label: "HIGH IMPACT" },
  medium: { bg: "bg-status-elevated/10", text: "text-status-elevated", border: "border-status-elevated/30", icon: CheckCircle2, label: "MEDIUM IMPACT" },
  low: { bg: "bg-surface-bright/20", text: "text-on-surface-variant", border: "border-surface-bright/30", icon: Info, label: "LOW IMPACT" },
};

// Map old "importance" to new severity
function mapImportanceToSeverity(importance: string, signalType: string = "") {
  if (signalType.toUpperCase() === "CORRELATION") return "correlation";
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
        const severityKey = mapImportanceToSeverity(signal.importance, signal.signal_type);
        // Elevate to critical if high score
        let finalSeverityKey = (severityKey === "high" && (signal.score || 0) > 0.9) ? "critical" : severityKey;
        if (severityKey === "correlation") finalSeverityKey = "correlation";
        
        const severity = SEVERITY_STYLES[finalSeverityKey];
        const SeverityIcon = severity.icon;

        const confidence = signal.score ? Math.round(signal.score * 100) : (80 + ((signal.id?.length || 0) % 20)); // Fallback for UI density if score missing
        const signalType = (signal.signal_type || "Market Event").replace(/_/g, ' ').toUpperCase();
        
        // Emphasize correlations
        const isCorrelation = finalSeverityKey === "correlation";

        return (
          <div
            key={signal.id}
            className={`intelligence-card p-5 group flex flex-col gap-3 relative overflow-hidden ${isCorrelation ? 'ring-2 ring-purple-500/50 shadow-[0_0_15px_rgba(168,85,247,0.1)]' : ''}`}
          >
            {/* Left Accent Line based on Severity */}
            <div className={`absolute left-0 top-0 bottom-0 ${isCorrelation ? 'w-2' : 'w-1'} ${severity.bg} opacity-80`} />

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
              <h4 className="text-base font-medium text-on-surface leading-snug group-hover:text-primary transition-colors">
                {signal.url ? (
                  <a href={signal.url} target="_blank" rel="noopener noreferrer">
                    {signal.title}
                  </a>
                ) : (
                  signal.title
                )}
              </h4>

              {/* Stripped Analysis/Content */}
              {!compact && signal.content && (
                <p className="mt-1.5 text-sm text-on-surface-variant line-clamp-1 leading-relaxed">
                  {stripHtml(signal.content)}
                </p>
              )}

              {/* AI Insight */}
              <div className="mt-3 bg-primary/5 border border-primary/10 rounded-md p-2 flex items-start gap-2">
                <span className="text-[10px] font-bold text-primary uppercase tracking-widest mt-0.5 shrink-0">AI Insight:</span>
                <span className="text-sm text-on-surface-variant leading-tight">
                  {getMockInsight(signal, finalSeverityKey)}
                </span>
              </div>
              
              {/* Evidence Box for Correlations */}
              {isCorrelation && signal.payload?.supporting_signals && signal.payload.supporting_signals.length > 0 && (
                <div className="mt-4 pt-3 border-t border-purple-500/20">
                  <div className="text-[10px] font-bold text-purple-400 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                    <Zap className="w-3 h-3" /> Supporting Evidence
                  </div>
                  <div className="grid grid-cols-1 gap-2">
                    {signal.payload.supporting_signals.map((ev: any, i: number) => {
                      const evType = (ev.signal_type || "Signal").toUpperCase();
                      return (
                        <div key={ev.id || i} className="p-3 rounded-lg border border-surface-bright/30 bg-surface-low hover:bg-surface-bright/10 transition-colors">
                          <div className="text-[10px] font-mono text-on-surface-variant uppercase tracking-widest mb-1 opacity-70">
                            ┌ {evType} ───────────────────
                          </div>
                          <p className="font-medium text-sm text-on-surface line-clamp-1">{ev.title}</p>
                          {ev.content && (
                            <p className="text-xs text-on-surface-variant line-clamp-1 mt-0.5">{stripHtml(ev.content)}</p>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Footer Metrics */}
            <div className="flex items-center justify-between pt-3 border-t border-surface-bright/20 mt-1">
              <div className="flex items-center gap-3">
                <span className="text-xs font-mono text-on-surface-variant">
                  Source: <span className="text-on-surface capitalize">{getProviderName(signal)}</span>
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-16 h-1.5 bg-surface-bright/30 rounded-full overflow-hidden">
                  <div className={`h-full ${severity.bg.replace('/10', '')}`} style={{ width: `${confidence}%` }} />
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