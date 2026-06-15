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