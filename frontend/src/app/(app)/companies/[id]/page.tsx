"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getCompanyDetail, triggerMonitoring, getCompanyAnalytics, getRankings } from "@/lib/api";
import type { CompanyDetailResponse, CompanyAnalytics } from "@/lib/types";
import SignalFeed from "@/components/SignalFeed";
import { ArrowLeft, RefreshCw, Activity, ExternalLink, Globe, Play, FileText, BarChart3, AlertCircle } from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function CompanyDetailPage() {
  const { id } = useParams() as { id: string };
  const [data, setData] = useState<CompanyDetailResponse | null>(null);
  const [analytics, setAnalytics] = useState<CompanyAnalytics | null>(null);
  const [rank, setRank] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [monitoring, setMonitoring] = useState(false);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [res, analyticsData, rankingsData] = await Promise.all([
          getCompanyDetail(id),
          getCompanyAnalytics(id),
          getRankings(100)
        ]);
        setData(res);
        setAnalytics(analyticsData);
        const myRank = rankingsData.find(r => r.id === id)?.rank;
        if (myRank) setRank(myRank);
      } catch (err) {
        console.error("Failed to load company detail", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  const handleMonitor = async () => {
    setMonitoring(true);
    try {
      await triggerMonitoring(id);
      // Wait a bit, then reload
      setTimeout(async () => {
        try {
          const res = await getCompanyDetail(id);
          setData(res);
        } catch (e) {}
      }, 2000);
    } catch (err) {
      console.error("Failed to trigger monitoring", err);
    } finally {
      setMonitoring(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="skeleton h-8 w-48 mb-6" />
        <div className="skeleton h-32 w-full" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 skeleton h-96" />
          <div className="skeleton h-96" />
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-12 text-center text-on-surface-variant">
        <AlertCircle className="w-12 h-12 mx-auto mb-4 opacity-20" />
        <p>Entity not found or system error.</p>
        <Link href="/companies" className="text-primary hover:underline mt-4 inline-block">Return to Entities</Link>
      </div>
    );
  }

  const { company, latest_report, recent_signals } = data;

  const score = company.intelligence_score || analytics?.current?.total || 0;
  const signalsCount = company.signals_count || recent_signals.length;
  
  let sentimentText = "Neutral";
  let sentimentColor = "text-status-elevated";
  let sentimentBorder = "border-l-status-elevated";