"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { addCompany } from "@/lib/api";
import { ArrowLeft, Loader2, Search, Target } from "lucide-react";
import Link from "next/link";

export default function AddCompanyPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [website, setWebsite] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await addCompany(name, website || undefined);
      router.push(`/companies/${result.company.id}`);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to add company";
      setError(message);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <Link href="/companies" className="inline-flex items-center gap-2 text-sm text-on-surface-variant hover:text-primary transition-colors mb-6">
        <ArrowLeft className="w-4 h-4" />
        Back to Companies
      </Link>

      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-on-surface">Target Acquisition</h1>
        <p className="text-sm text-on-surface-variant mt-2 leading-relaxed">
          Initialize monitoring for a new target company. Argos will auto-discover data sources, initialize tracking, and begin parsing real-time signals.
        </p>
      </div>

      <div className="glass-panel p-8 rounded-2xl relative overflow-hidden">
        {/* Decorative Grid Background */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />
        
        <form onSubmit={handleSubmit} className="relative space-y-6">
          {error && (
            <div className="p-4 rounded-lg bg-status-critical/10 border border-status-critical/30 text-status-critical text-sm flex items-start gap-3">
              <Target className="w-5 h-5 shrink-0" />
              <p>{error}</p>
            </div>
          )}

          <div className="space-y-2">
            <label className="text-xs font-mono text-on-surface-variant uppercase tracking-widest">
              Company Name <span className="text-status-critical">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-surface-lowest border border-surface-bright/50 rounded-lg px-4 py-3 text-sm text-on-surface focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all placeholder:text-on-surface-variant/50"
              placeholder="e.g. OpenAI"
              required
              disabled={loading}
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-mono text-on-surface-variant uppercase tracking-widest">
              Primary Domain (Optional)
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
                <Search className="h-4 w-4 text-on-surface-variant" />
              </div>
              <input
                type="url"
                value={website}
                onChange={(e) => setWebsite(e.target.value)}
                className="w-full bg-surface-lowest border border-surface-bright/50 rounded-lg pl-10 pr-4 py-3 text-sm text-on-surface focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all placeholder:text-on-surface-variant/50"
                placeholder="https://openai.com"
                disabled={loading}
              />
            </div>
            <p className="text-xs text-on-surface-variant mt-1.5">
              Providing a domain improves auto-discovery accuracy.
            </p>
          </div>

          <div className="pt-4 flex justify-end">
            <button
              type="submit"
              disabled={loading || !name}