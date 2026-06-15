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
  };

  const handleClose = () => {
    setName("");
    setWebsite("");
    setDiscovered(null);
    setError(null);
    setStep("input");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-lg mx-4 glass-card p-6 animate-slide-up">
        {/* Close Button */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 text-argos-text-dim hover:text-argos-text transition-colors"
        >
          ✕
        </button>

        {step === "input" ? (
          <>
            {/* Header */}
            <div className="mb-6">
              <h2 className="text-xl font-bold text-argos-text">
                Track New Company
              </h2>
              <p className="text-sm text-argos-text-dim mt-1">
                Argos will auto-discover all available data sources
              </p>
            </div>

            {/* Form */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-argos-text-muted mb-1.5">
                  Company Name *
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}