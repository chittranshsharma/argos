"use client";

import { useEffect, useState } from "react";
import { getStats, getSignalFeed, getShareOfVoice, getGlobalAnomalies } from "@/lib/api";
import type { DashboardStats, Signal, ShareOfVoiceEntry, Alert } from "@/lib/types";
import SignalFeed from "@/components/SignalFeed";
import { Activity, Zap, FileText, Globe } from "lucide-react";