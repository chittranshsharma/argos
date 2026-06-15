"use client";

import { useEffect, useState } from "react";
import { getAllReports, clearReports, getCompanies } from "@/lib/api";
import type { Report, Company } from "@/lib/types";
import { FileText, Download, Eye, ExternalLink, Trash2 } from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [targetCompanyId, setTargetCompanyId] = useState<string>("");

  const [isGenerating, setIsGenerating] = useState(false);
  const [isClearing, setIsClearing] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [reportsData, companiesData] = await Promise.all([
          getAllReports(),
          getCompanies()
        ]);
        setReports(reportsData);
        setCompanies(companiesData);
        
        if (reportsData.length > 0) {
          setSelectedReport(reportsData[0]);
          setTargetCompanyId(reportsData[0].company_id);
        } else if (companiesData.length > 0) {
          setTargetCompanyId(companiesData[0].id);
        }
      } catch (err) {
        console.error("Failed to load data", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleGenerate = async () => {
    if (!targetCompanyId) return;
    setIsGenerating(true);
    const startCount = reports.length;
    try {
      await fetch(`http://localhost:8001/companies/${targetCompanyId}/reports/generate`, {
        method: "POST"
      });
      
      // Poll every 2 seconds for up to 30 seconds
      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts++;
        try {
          const data = await getAllReports();
          if (data.length > startCount) {
            setReports(data);
            setSelectedReport(data[0]);
            setTargetCompanyId(data[0].company_id);
            setIsGenerating(false);
            clearInterval(pollInterval);
          } else if (attempts >= 15) {
            setIsGenerating(false);
            clearInterval(pollInterval);
            console.error("Report generation timed out or failed silently.");
          }
        } catch (e) {
          console.error("Polling failed", e);
        }
      }, 2000);

    } catch (err) {
      console.error(err);
      setIsGenerating(false);
    }
  };

  const handleClearAll = async () => {
    if (!confirm("Are you sure you want to clear all reports? This action cannot be undone.")) return;
    setIsClearing(true);
    try {
      await clearReports();
      setReports([]);
      setSelectedReport(null);
    } catch (err) {
      console.error("Failed to clear reports", err);
    } finally {
      setIsClearing(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!selectedReport) return;
    const element = document.getElementById("report-content");
    if (!element) return;
    
    try {
      const html2pdf = (await import("html2pdf.js")).default;
      const opt = {
        margin:       0.5,
        filename:     `${selectedReport.company_name}_Intelligence_Briefing.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true, backgroundColor: '#0a0a0a' }, // match background
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
      };
      
      html2pdf().set(opt).from(element).save();
    } catch (err) {
      console.error("Failed to generate PDF", err);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      <div className="flex items-center justify-between mb-6 shrink-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-on-surface flex items-center gap-3">
            <FileText className="w-8 h-8 text-primary" /> Briefings
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Executive summaries and automated intelligence reports.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={handleClearAll}
            disabled={isClearing || reports.length === 0}
            suppressHydrationWarning
            className={`flex items-center gap-2 font-bold px-4 py-2 rounded-lg transition-colors ${
              isClearing || reports.length === 0 
                ? 'bg-status-danger/20 text-status-danger/50 cursor-not-allowed' 
                : 'bg-status-danger/20 text-status-danger hover:bg-status-danger/30 border border-status-danger/50'
            }`}
            title="Delete all reports"
          >
            <Trash2 className="w-4 h-4" />
            {isClearing ? "Clearing..." : "Clear All"}
          </button>
          
          <div className="flex items-center gap-2 bg-surface-low border border-surface-bright/30 p-1 rounded-xl">
            <select 
              value={targetCompanyId}
              onChange={(e) => setTargetCompanyId(e.target.value)}
              className="bg-transparent border-none text-sm text-on-surface px-3 py-1 focus:outline-none focus:ring-0 w-36 truncate"
            >
              <option value="" disabled>Select target...</option>
              {companies.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
            <button 
              onClick={handleGenerate}
              disabled={!targetCompanyId || isGenerating}
              suppressHydrationWarning
              className={`flex items-center gap-2 font-bold px-4 py-2 rounded-lg transition-colors ${
                !targetCompanyId || isGenerating 
                  ? 'bg-primary/50 text-black/50 cursor-not-allowed' 
                  : 'bg-primary text-black hover:bg-primary-hover'
              }`}
              title={!targetCompanyId ? "Select a company first" : "Generate new report"}
            >
              <FileText className="w-4 h-4" />
              {isGenerating ? "Generating..." : "Generate New"}
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Report List */}
        <div className="w-1/3 shrink-0 flex flex-col gap-3 overflow-y-auto pr-2">
          {loading ? (
            [...Array(5)].map((_, i) => (
              <div key={i} className="skeleton h-24 w-full" />
            ))
          ) : reports.length > 0 ? (
            reports.map((report) => (
              <button
                key={report.id}
                onClick={() => setSelectedReport(report)}
                className={`text-left p-4 rounded-xl border transition-all ${
                  selectedReport?.id === report.id
                    ? "bg-primary/10 border-primary"
                    : "bg-surface-low border-surface-bright/20 hover:border-primary/50"