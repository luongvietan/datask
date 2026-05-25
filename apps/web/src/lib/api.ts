/**
 * Datask REST API client for the Next.js frontend.
 * Calls go to /api/v1/* which next.config.ts proxies to the FastAPI backend.
 */

const BASE = "/api/v1";

export class ApiError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  init?: RequestInit & { apiKey?: string }
): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(init?.apiKey ? { Authorization: `Bearer ${init.apiKey}` } : {}),
    ...init?.headers,
  };

  const res = await fetch(`${BASE}${path}`, { ...init, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(
      body.error ?? "unknown_error",
      body.message ?? `HTTP ${res.status}`,
      res.status
    );
  }

  return res.json() as Promise<T>;
}

// ---- Account ----

export const createAccount = (email: string) =>
  request<{ id: string; email: string; tier: string }>("/account", {
    method: "POST",
    body: JSON.stringify({ email }),
  });

// ---- API Keys ----

export const listKeys = (apiKey: string) =>
  request<ApiKeyOut[]>("/keys", { apiKey });

export const createKey = (apiKey: string, label: string) =>
  request<ApiKeyOut & { key: string }>("/keys", {
    method: "POST",
    apiKey,
    body: JSON.stringify({ label }),
  });

export const revokeKey = (apiKey: string, keyId: string) =>
  request<void>(`/keys/${keyId}`, { method: "DELETE", apiKey });

// ---- Billing ----

export const getUsage = (apiKey: string) =>
  request<UsageSummaryOut>("/billing/usage", { apiKey });

export const createCheckout = (apiKey: string) =>
  request<{ checkout_url: string }>("/billing/checkout", {
    method: "POST",
    apiKey,
  });

// ---- Types ----

export interface ApiKeyOut {
  id: string;
  label: string;
  key_preview: string;
  created_at: string;
  is_active: boolean;
}

export interface UsageSummaryOut {
  current_month_requests: number;
  successful_requests: number;
  failed_requests: number;
  credits_used: number;
  quota_remaining: number | null;
  tier: string;
  billing_period_end: string | null;
  budget: number | null;
  remaining: number | null;
  resets_at: string | null;
  alert_threshold: number;
  used: number;
}

// ---- Budget ----

export const setBudget = (apiKey: string, budget: number | null, threshold: number = 80) =>
  request<BudgetOut>("/billing/budget", {
    method: "PATCH",
    apiKey,
    body: JSON.stringify({
      monthly_credit_budget: budget,
      budget_alert_threshold: threshold,
    }),
  });

export interface BudgetOut {
  monthly_credit_budget: number | null;
  budget_alert_threshold: number;
  used: number;
  budget: number | null;
  remaining: number | null;
  resets_at: string | null;
  alert_threshold: number;
}

// ---- Request Log ----

export interface ListRequestsParams {
  limit?: number;
  offset?: number;
  layer?: number | null;
  success?: boolean | null;
}

export const listRequests = (
  apiKey: string,
  params: ListRequestsParams = {}
) => {
  const query = new URLSearchParams();
  if (params.limit != null) query.set("limit", String(params.limit));
  if (params.offset != null) query.set("offset", String(params.offset));
  if (params.layer != null) query.set("layer", String(params.layer));
  if (params.success != null) query.set("success", String(params.success));
  return request<import("@/types").RequestLogResponse>(
    `/requests?${query.toString()}`,
    { apiKey }
  );
};
