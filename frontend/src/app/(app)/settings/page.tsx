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