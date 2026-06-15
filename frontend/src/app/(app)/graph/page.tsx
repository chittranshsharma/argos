"use client";

import { useEffect, useState, useRef } from "react";
import dynamic from "next/dynamic";
import { getCompanies } from "@/lib/api";
import { Network, Info, ZoomIn, ZoomOut, Maximize, Filter, CheckCircle2, ArrowRight, FileText, Activity } from "lucide-react";
import type { GraphData, GraphNode, GraphLink } from "@/components/graph/GraphRenderer";
import Link from "next/link";