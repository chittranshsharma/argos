/**
 * Argos — API Client
 * All functions matching backend endpoints.
 */

import type {
  Company,
  Signal,
  Report,
  DashboardStats,
  CompanyDetailResponse,
  MonitoringStatus,
  DiscoveryResult,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

// ── Generic fetch wrapper ──────────────────────────────────

async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorBody = await res.text().catch(() => "Unknown error");
    throw new Error(`API Error ${res.status}: ${errorBody}`);
  }

  return res.json();
}

// ── Health ──────────────────────────────────────────────────

export async function getHealth() {
  return apiFetch<{ status: string; companies_tracked: number; signals_today: number }>("/health");
}

// ── Stats ──────────────────────────────────────────────────

export async function getStats(): Promise<DashboardStats> {
  return apiFetch<DashboardStats>("/stats");
}

// ── Companies ──────────────────────────────────────────────

export async function getCompanies(): Promise<Company[]> {
  const data = await apiFetch<{ companies: Company[] }>("/companies");
  return data.companies;
}

export async function getCompanyDetail(
  id: string
): Promise<CompanyDetailResponse> {
  return apiFetch<CompanyDetailResponse>(`/companies/${id}`);
}

export async function addCompany(
  name: string,
  website?: string
): Promise<{ company: Company; discovered_sources: DiscoveryResult }> {
  return apiFetch<{ company: Company; discovered_sources: DiscoveryResult }>(
    "/companies",
    {
      method: "POST",
      body: JSON.stringify({ name, website }),
    }
  );
}

export async function deleteCompany(id: string): Promise<void> {
  await apiFetch(`/companies/${id}`, { method: "DELETE" });
}

export async function triggerMonitoring(
  id: string
): Promise<MonitoringStatus> {
  return apiFetch<MonitoringStatus>(`/companies/${id}/monitor`, {
    method: "POST",
  });
}

export async function getCompetitors(companyId: string): Promise<{
  company_name: string;
  competitors: string[];
}> {
  try {
    const res = await apiFetch<{ company_name: string; competitors: string[] }>(`/companies/${companyId}/competitors`);
    return res;
  } catch {
    return { company_name: '', competitors: [] };
  }
}

// ── Signals ────────────────────────────────────────────────

export async function getCompanySignals(
  companyId: string,
  limit = 50,
  source = "all"
): Promise<Signal[]> {
  const params = new URLSearchParams({ limit: String(limit), source });
  const data = await apiFetch<{ signals: Signal[] }>(
    `/companies/${companyId}/signals?${params}`
  );
  return data.signals;
}

export async function getSignalFeed(params?: {
  limit?: number;
  source?: string;
  importance?: string;
  company_id?: string;
}): Promise<Signal[]> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.source) searchParams.set("source", params.source);
  if (params?.importance) searchParams.set("importance", params.importance);
  if (params?.company_id) searchParams.set("company_id", params.company_id);

  const data = await apiFetch<{ signals: Signal[] }>(
    `/signals/feed?${searchParams}`
  );
  return data.signals;
}

// ── Reports ────────────────────────────────────────────────

export async function getCompanyReports(
  companyId: string
): Promise<Report[]> {
  const data = await apiFetch<{ reports: Report[] }>(
    `/companies/${companyId}/reports`
  );
  return data.reports;
}

export async function getAllReports(companyId?: string): Promise<Report[]> {
  const url = companyId ? `/reports?company_id=${companyId}` : "/reports";
  const data = await apiFetch<{ reports: Report[] }>(url);
  return data.reports;
}

export async function clearReports(): Promise<void> {
  await apiFetch("/reports", { method: "DELETE" });
}

// ── Analytics ──────────────────────────────────────────────