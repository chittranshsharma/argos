"use client";

import type { Importance } from "@/lib/types";

// ── Component ──────────────────────────────────────────────

interface AlertBadgeProps {
  importance: Importance;
  count?: number;
  size?: "sm" | "md" | "lg";
}

const STYLES: Record<Importance, { bg: string; dot: string; text: string }> = {
  high: {
    bg: "bg-argos-danger/10 border-argos-danger/30",
    dot: "bg-argos-danger",
    text: "text-argos-danger",
  },
  medium: {
    bg: "bg-argos-warning/10 border-argos-warning/30",
    dot: "bg-argos-warning",
    text: "text-argos-warning",
  },
  low: {
    bg: "bg-argos-surface-3 border-argos-border",
    dot: "bg-argos-text-dim",
    text: "text-argos-text-dim",
  },
};

const SIZE_STYLES: Record<string, string> = {
  sm: "px-1.5 py-0.5 text-[10px]",
  md: "px-2 py-1 text-xs",
  lg: "px-3 py-1.5 text-sm",
};

export default function AlertBadge({
  importance,
  count,
  size = "sm",
}: AlertBadgeProps) {
  const style = STYLES[importance] || STYLES.low;
  const sizeStyle = SIZE_STYLES[size] || SIZE_STYLES.sm;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium uppercase tracking-wider ${style.bg} ${style.text} ${sizeStyle}`}
    >
      {importance === "high" && (
        <span className="relative flex h-1.5 w-1.5">
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full ${style.dot} opacity-75`}
          />
          <span
            className={`relative inline-flex h-1.5 w-1.5 rounded-full ${style.dot}`}
          />
        </span>
      )}
      {importance}
      {count !== undefined && count > 0 && (
        <span className="font-bold">{count}</span>
      )}
    </span>
  );
}