// Shared TypeScript types for Datask web app

export type Tier = "free" | "payg" | "commit_10k" | "commit_100k";

export type Layer = 1 | 2 | 3;

export type RequestStatus = "success" | "failed" | "queued" | "processing";

export interface Account {
  id: string;
  email: string;
  tier: Tier;
  stripe_customer_id: string | null;
  created_at: string;
}

export interface ApiKey {
  id: string;
  label: string;
  key_preview: string;  // "dtsk_live_a3f9..." — prefix only, never full
  is_active: boolean;
  created_at: string;
  last_used_at: string | null;
}

export interface UsageRecord {
  id: string;
  url: string;
  layer: Layer;
  status: RequestStatus;
  credits_used: number;
  response_time_ms: number | null;
  error_code: string | null;
  created_at: string;
}

export interface RequestLogItem {
  request_id: string | null;
  url: string;
  domain: string | null;
  layer: Layer;
  success: boolean;
  credits_used: number;
  response_time_ms: number | null;
  validation_valid: boolean | null;
  created_at: string | null;
}

export interface RequestLogResponse {
  requests: RequestLogItem[];
  total: number;
}

export interface UsageSummary {
  current_month_requests: number;
  successful_requests: number;
  failed_requests: number;
  credits_used: number;
  quota_remaining: number | null;
  tier: Tier;
  billing_period_end: string | null;
}
