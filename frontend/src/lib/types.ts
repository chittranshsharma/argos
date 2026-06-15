/**
 * Argos — TypeScript Type Definitions
 */

// ── Company ────────────────────────────────────────────────

export interface Company {
  id: string;
  name: string;
  website: string | null;
  github_org: string | null;
  careers_url: string | null;
  reddit_sub: string | null;
  producthunt_slug: string | null;
  linkedin_url: string | null;
  changelog_url: string | null;
  news_keywords: string[] | null;
  added_at: string;
  last_monitored: string | null;
  is_active: boolean;
  competitors?: string[];
  intelligence_score?: number;
  score_change?: number;
  signals_count?: number;
}

export interface AnalyticsPayload {
  signal_volume: number;
  hiring_velocity: number;
  funding_activity: number;
  sentiment: number;
  executive_events: number;
  report_activity: number;
  total: number;
}

export interface AnalyticsHistoryRecord {
  payload_json: AnalyticsPayload;
  timestamp: string;
}

export interface CompanyAnalytics {
  current: AnalyticsPayload | null;
  history: AnalyticsHistoryRecord[];
}

export interface RankingEntry {
  company: string;
  score: number;
  change: number;
  rank: number;
  signals: number;
  id: string;
  website: string | null;
}

// ── Signal ─────────────────────────────────────────────────
