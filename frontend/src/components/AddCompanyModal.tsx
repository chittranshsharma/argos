"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { addCompany } from "@/lib/api";
import type { DiscoveryResult } from "@/lib/types";

// ── Source Display Config ──────────────────────────────────

const SOURCE_LABELS: { key: keyof DiscoveryResult; label: string; icon: string }[] = [
  { key: "github_org", label: "GitHub", icon: "◆" },
  { key: "careers_url", label: "Careers", icon: "◈" },
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
  const [addedCompanyId, setAddedCompanyId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const [step, setStep] = useState<"input" | "discovered">("input");

  if (!isOpen) return null;

  const handleDiscover = async () => {
    if (!name.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const result = await addCompany(name.trim(), website.trim() || undefined);
      setDiscovered(result.discovered_sources);
      setAddedCompanyId(result.company?.id || null);
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
                  placeholder="e.g. Zerodha"
                  className="w-full rounded-xl bg-argos-surface-2 border border-argos-border px-4 py-3 text-sm text-argos-text placeholder:text-argos-text-dim focus:border-argos-accent focus:outline-none focus:ring-1 focus:ring-argos-accent/30 transition-all"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-argos-text-muted mb-1.5">
                  Website URL
                  <span className="text-argos-text-dim font-normal ml-1">(optional)</span>
                </label>
                <input
                  type="url"
                  value={website}
                  onChange={(e) => setWebsite(e.target.value)}
                  placeholder="https://example.com"
                  className="w-full rounded-xl bg-argos-surface-2 border border-argos-border px-4 py-3 text-sm text-argos-text placeholder:text-argos-text-dim focus:border-argos-accent focus:outline-none focus:ring-1 focus:ring-argos-accent/30 transition-all"
                />
              </div>

              {error && (
                <div className="rounded-xl bg-argos-danger/10 border border-argos-danger/30 px-4 py-3 text-sm text-argos-danger">
                  {error}
                </div>
              )}

              <button
                onClick={handleDiscover}
                disabled={!name.trim() || loading}
                className="w-full rounded-xl bg-argos-accent hover:bg-argos-accent-hover disabled:opacity-50 disabled:cursor-not-allowed px-4 py-3 text-sm font-semibold text-white transition-all duration-200 hover:shadow-lg hover:shadow-argos-accent/20"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Discovering sources for {name}...
                  </span>
                ) : (
                  "Discover & Track"
                )}
              </button>
            </div>
          </>
        ) : (
          <>
            {/* Discovery Results */}
            <div className="mb-6">
              <h2 className="text-xl font-bold text-argos-text">
                Sources Discovered ✓
              </h2>
              <p className="text-sm text-argos-text-dim mt-1">
                {name} has been added and monitoring has started
              </p>
            </div>

            <div className="space-y-2 mb-6">
              {SOURCE_LABELS.map(({ key, label, icon }) => {
                const value = discovered?.[key];
                const isActive =
                  value !== null &&
                  value !== undefined &&
                  value !== "" &&
                  (Array.isArray(value) ? value.length > 0 : true);

                return (
                  <div
                    key={key}
                    className={`flex items-center gap-3 rounded-xl px-4 py-2.5 border ${
                      isActive
                        ? "bg-argos-success/5 border-argos-success/20 text-argos-success"
                        : "bg-argos-surface-2/50 border-argos-border/50 text-argos-text-dim"
                    }`}
                  >
                    <span className="text-sm">{icon}</span>
                    <span className="text-sm font-medium flex-1">{label}</span>
                    <span className="text-xs">
                      {isActive ? (
                        <span className="flex items-center gap-1">
                          <span>✓</span>
                          <span className="text-argos-text-dim truncate max-w-[150px]">
                            {Array.isArray(value) ? value.join(", ") : String(value)}
                          </span>
                        </span>
                      ) : (
                        "Not found"
                      )}
                    </span>
                  </div>
                );
              })}
            </div>

            <button
              onClick={handleClose}
              className="w-full rounded-xl bg-argos-accent hover:bg-argos-accent-hover px-4 py-3 text-sm font-semibold text-white transition-all duration-200"
            >
              Done
            </button>
          </>
        )}
      </div>
    </div>
  );
}