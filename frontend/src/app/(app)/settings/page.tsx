"use client";

import { Settings as SettingsIcon, Link2, Database, Key, Shield, HardDrive } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-on-surface flex items-center gap-3">
          <SettingsIcon className="w-8 h-8 text-primary" /> Configuration
        </h1>
        <p className="text-sm text-on-surface-variant mt-2">
          Manage system preferences, integrations, and data sources.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-4">
        
        {/* Navigation Sidebar */}
        <div className="flex flex-col gap-2">
          <button className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-colors bg-primary/10 text-primary border border-primary/20">
            <Database className="w-4 h-4" /> Data Sources
          </button>
          <button className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-on-surface-variant hover:bg-surface-bright/20 transition-colors">
            <Key className="w-4 h-4" /> API Keys
          </button>
          <button className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-on-surface-variant hover:bg-surface-bright/20 transition-colors">
            <Shield className="w-4 h-4" /> Security
          </button>
        </div>

        {/* Content Area */}
        <div className="md:col-span-2 space-y-6">
          <div className="intelligence-card p-6">
            <div className="flex items-center justify-between border-b border-surface-bright/20 pb-4 mb-4">
              <div>
                <h2 className="text-lg font-semibold text-on-surface">Data Sources</h2>
                <p className="text-sm text-on-surface-variant">Active connections to intelligence providers.</p>
              </div>
              <div className="px-3 py-1 rounded bg-status-critical/10 text-status-critical border border-status-critical/30 text-xs font-mono">
                API OFFLINE
              </div>
            </div>

            <p className="text-sm text-on-surface-variant mb-6 p-4 bg-surface-bright/10 rounded-lg border border-surface-bright/20">
              Endpoint Missing: GET /api/v1/system/sources<br/>
              The backend configuration endpoints are not currently active. Below is a UI demonstration of the planned structure.
            </p>

            <div className="space-y-4">
              {[
                { name: "GitHub API", status: "Connected", sync: "10m ago", icon: HardDrive },
                { name: "Reddit OAuth", status: "Connected", sync: "2m ago", icon: Link2 },
                { name: "LinkedIn Scraper", status: "Degraded", sync: "1h ago", icon: Database },
                { name: "HackerNews Firehose", status: "Connected", sync: "Just now", icon: HardDrive },
              ].map((source, i) => {
                const Icon = source.icon;
                const isDegraded = source.status === "Degraded";
                return (
                  <div key={i} className="flex items-center justify-between p-4 rounded-lg bg-surface-lowest border border-surface-bright/30">
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-lg ${isDegraded ? 'bg-status-elevated/10 text-status-elevated' : 'bg-status-success/10 text-status-success'}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="font-medium text-on-surface text-sm">{source.name}</h4>
                        <p className="text-xs text-on-surface-variant mt-0.5">Last Sync: {source.sync}</p>
                      </div>
                    </div>
                    <button className="text-sm text-on-surface-variant hover:text-primary transition-colors">
                      Configure
                    </button>
                  </div>
                )
              })}
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}