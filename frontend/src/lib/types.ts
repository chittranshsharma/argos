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

export type SignalSource =
  | "github"
  | "news"
  | "reddit"
  | "hackernews"
  | "linkedin"
  | "jobs"
  | "changelog"
  | "producthunt";

export type Importance = "high" | "medium" | "low";

export interface Signal {
  id: string;
  company_id: string;
  company_name: string;
  source: SignalSource;
  signal_type: string;
  title: string;
  content?: string | null;
  importance: "low" | "medium" | "high";
  url?: string | null;
  collected_at: string;
  score?: number;
}

export interface Anomaly {
  source: string;
  is_anomaly: boolean;
  ratio: number;
  message: string;
}

// ── Report ─────────────────────────────────────────────────

export interface Report {
  id: string;
  company_id: string;
  company_name: string;
  report_markdown: string;
  signals_analyzed: number;
  key_findings: string[];
  hiring_trends: HiringTrend[];
  tech_signals: TechSignal[];
  generated_at: string;
  period_start: string;
  period_end: string;
}

export interface HiringTrend {
  role: string;
  count: number;
  trend: "growing" | "stable" | "declining";
}

export interface TechSignal {
  technology: string;
  signal_type: string;
  evidence: string;
}

// ── Alert ──────────────────────────────────────────────────

export interface Alert {
  id: string;
  company_id: string;
  company_name: string;
  alert_type: string;
  message: string;
  sent_via: string[];
  is_sent: boolean;
  created_at: string;
  confidence_score?: number;
  impact_level?: string;
}

// ── Discovery ──────────────────────────────────────────────

export interface DiscoveryResult {
  github_org: string | null;
  careers_url: string | null;
  reddit_sub: string | null;
  producthunt_slug: string | null;
  linkedin_url: string | null;
  changelog_url: string | null;
  news_keywords: string[];
}

// ── API Responses ──────────────────────────────────────────

export interface MonitoringStatus {
  message: string;
  status: "running" | "completed" | "failed";
}

export interface DashboardStats {
  companies_tracked: number;
  signals_today: number;
  high_priority_alerts: number;
  reports_generated: number;
}

export interface ScoreBreakdown {
  signal_volume: number;
  hiring_velocity: number;
  funding_activity: number;
  sentiment: number;
  executive_events: number;
  report_activity: number;
  total: number;
}

export interface CompanyDetailResponse {
  company: Company;
  latest_report: Report | null;
  recent_signals: Signal[];
  graph_data: GraphData;
  score_breakdown?: ScoreBreakdown;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface GraphNode {
  id: string;
  name: string;
  type: string;
  description: string;
}

export interface GraphLink {
  source: string;
  target: string;
  relation: string;
}

// ── Market Analytics ───────────────────────────────────────

export interface VelocityEntry {
  date: string;
  hiring: number;
  funding: number;
  launches: number;
  news: number;
  executive: number;
}

export interface SentimentEntry {
  company_name: string;
  sentiment_score: number;
}

export interface GlobalKPIs {
  tracked_companies: number;
  signals_analyzed: number;
  critical_events: number;
  average_sentiment: number;
}

export interface ShareOfVoiceEntry {
  company: string;
  volume: number;
  percentage: number;
}

export interface DistributionEntry {
  category: string;
  count: number;
}

export interface Hypothesis {
  id: string;
  company_id: string;
  type: string;
  title: string;
  description: string;
  themes: string[];
  confidence: number;
  status: string;
  updated_at: string;
}

export interface HypothesisEvaluation {
  id: string;
  hypothesis_id: string;
  signal_id: string;
  impact: number;
  reasoning: string;
  created_at: string;
  signals?: Signal; // The joined signal
}