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