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
