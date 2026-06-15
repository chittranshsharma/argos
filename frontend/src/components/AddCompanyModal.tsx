"use client";

import { useState } from "react";
import { addCompany } from "@/lib/api";
import type { DiscoveryResult } from "@/lib/types";

// ── Source Display Config ──────────────────────────────────

const SOURCE_LABELS: { key: keyof DiscoveryResult; label: string; icon: string }[] = [
  { key: "github_org", label: "GitHub", icon: "◆" },
  { key: "careers_url", label: "Careers", icon: "◈" },
  { key: "reddit_sub", label: "Reddit", icon: "◉" },
  { key: "producthunt_slug", label: "ProductHunt", icon: "▣" },
  { key: "linkedin_url", label: "LinkedIn", icon: "▢" },
  { key: "changelog_url", label: "Changelog", icon: "◎" },
  { key: "news_keywords", label: "News Keywords", icon: "◇" },
];

// ── Component ──────────────────────────────────────────────

interface AddCompanyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function AddCompanyModal({
  isOpen,
  onClose,
  onSuccess,
}: AddCompanyModalProps) {
  const [name, setName] = useState("");
  const [website, setWebsite] = useState("");
  const [loading, setLoading] = useState(false);
  const [discovered, setDiscovered] = useState<DiscoveryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<"input" | "discovered">("input");

  if (!isOpen) return null;

  const handleDiscover = async () => {
    if (!name.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const result = await addCompany(name.trim(), website.trim() || undefined);
      setDiscovered(result.discovered_sources);
      setStep("discovered");
      onSuccess();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Discovery failed";
      setError(message);
    } finally {
      setLoading(false);
    }