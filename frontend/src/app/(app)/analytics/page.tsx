"use client";

import { useEffect, useState } from "react";
import { 
  LineChart, Activity, ShieldAlert, BarChart3,
  Globe, AlertTriangle, Building2, Zap, ArrowUpRight, ArrowDownRight, Minus, Radar
} from "lucide-react";
import { 
  getGlobalKPIs, getGlobalVelocity, getGlobalSentiment, getGlobalAnomalies, getRankings,
  getShareOfVoice, getIntelligenceDistribution
} from "@/lib/api";
import type { 
  GlobalKPIs, VelocityEntry, SentimentEntry, Alert, RankingEntry, ShareOfVoiceEntry, DistributionEntry 
} from "@/lib/types";
import { 