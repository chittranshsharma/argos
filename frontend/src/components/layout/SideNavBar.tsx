"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Activity, 
  Network, 
  LineChart, 
  FileText, 
  Plus,
  ShieldAlert,
  Briefcase,
  Target
} from "lucide-react";
import { cn } from "@/lib/utils";

const CORE_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/strategy", label: "Strategy Portfolio", icon: Briefcase },
  { href: "/companies", label: "Companies", icon: Activity },
  { href: "/intelligence", label: "Intelligence Stream", icon: Activity },
];

const ANALYSIS_ITEMS = [
  { href: "/scorecard", label: "Analyst Scorecard", icon: Target },
  { href: "/graph", label: "Knowledge Graph", icon: Network },
  { href: "/analytics", label: "Analytics", icon: LineChart },
  { href: "/reports", label: "Reports", icon: FileText },
];

const ADMIN_ITEMS = [
  { href: "/admin/intelligence-review", label: "Review Queue", icon: ShieldAlert },
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
          </div>
          <span className="text-lg font-bold tracking-tight text-on-surface">
            Argos
          </span>
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto py-6 px-3 flex flex-col gap-6">
        <div className="px-3">
          <Link 
            href="/companies/new"
            className="flex items-center justify-center gap-2 w-full bg-primary text-black font-bold px-4 py-2 rounded-lg hover:scale-[1.02] active:scale-95 transition-transform"
          >
            <Plus className="w-4 h-4" />
            Add Company
          </Link>
        </div>

        <nav className="flex flex-col gap-1">
          <div className="px-3 pb-2 font-mono text-xs text-on-surface-variant uppercase tracking-widest">
            Core Systems
          </div>
          {CORE_ITEMS.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            const Icon = item.icon;
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                  isActive 
                    ? "bg-primary/10 text-primary border-l-2 border-primary rounded-l-none" 
                    : "text-on-surface-variant hover:text-on-surface hover:bg-white/5"
                )}
              >
                <Icon className="w-4 h-4" />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <nav className="flex flex-col gap-1 mt-4">
          <div className="px-3 pb-2 font-mono text-xs text-on-surface-variant uppercase tracking-widest">
            Analysis
          </div>
          {ANALYSIS_ITEMS.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            const Icon = item.icon;
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                  isActive 
                    ? "bg-primary/10 text-primary border-l-2 border-primary rounded-l-none" 
                    : "text-on-surface-variant hover:text-on-surface hover:bg-white/5"
                )}
              >
                <Icon className="w-4 h-4" />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <nav className="flex flex-col gap-1 mt-4">
          <div className="px-3 pb-2 font-mono text-xs text-on-surface-variant uppercase tracking-widest">
            Administration
          </div>
          {ADMIN_ITEMS.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            const Icon = item.icon;
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                  isActive 
                    ? "bg-red-900/30 text-red-400 border-l-2 border-red-500 rounded-l-none" 
                    : "text-on-surface-variant hover:text-on-surface hover:bg-white/5"
                )}
              >
                <Icon className="w-4 h-4" />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

      </div>
    </aside>
  );
}