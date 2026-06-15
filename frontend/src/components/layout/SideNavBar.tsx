"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Activity, 
  Network, 
  LineChart, 
  FileText, 
  Plus
} from "lucide-react";
import { cn } from "@/lib/utils";

const CORE_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/companies", label: "Companies", icon: Activity },
  { href: "/intelligence", label: "Intelligence Stream", icon: Activity },
];

const ANALYSIS_ITEMS = [
  { href: "/graph", label: "Knowledge Graph", icon: Network },
  { href: "/analytics", label: "Analytics", icon: LineChart },
  { href: "/reports", label: "Reports", icon: FileText },
];


export function SideNavBar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 bottom-0 z-40 w-64 border-r border-surface-bright/30 bg-surface flex flex-col">
      <div className="h-16 flex items-center px-6 border-b border-surface-bright/30">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="relative flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 border border-primary/30 group-hover:bg-primary/20 transition-all duration-300">
            <span className="text-primary font-bold text-base">A</span>
            <div className="absolute inset-0 rounded-md bg-primary/5 animate-pulse-glow" />