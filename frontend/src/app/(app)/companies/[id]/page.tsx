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