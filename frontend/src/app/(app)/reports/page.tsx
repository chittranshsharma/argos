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