/**
 * Datask JavaScript/TypeScript SDK — v0.1
 *
 * Usage:
 *   import { DataskClient } from "datask";
 *   const client = new DataskClient({ apiKey: "dtsk_live_..." });
 *   const content = await client.fetch("https://example.com");
 *   const data = await client.extract("https://shop.com/product", { schema: { price: "number" } });
 */

export class DataskError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status: number
  ) {
    super(message);
    this.name = "DataskError";
  }
}

export class AuthenticationError extends DataskError {
  constructor(message: string) {
    super("invalid_api_key", message, 401);
    this.name = "AuthenticationError";
  }
}

export class QuotaExceededError extends DataskError {
  public readonly upgradeUrl?: string;
  constructor(message: string, upgradeUrl?: string) {
    super("quota_exceeded", message, 402);
    this.name = "QuotaExceededError";
    this.upgradeUrl = upgradeUrl;
  }
}

export class RateLimitError extends DataskError {
  public readonly retryAfter: number;
  constructor(message: string, retryAfter: number = 60) {
    super("rate_limited", message, 429);
    this.name = "RateLimitError";
    this.retryAfter = retryAfter;
  }
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type FieldSchemaType = "string" | "number" | "integer" | "boolean";

export interface ExtendedFieldSchema {
  type: FieldSchemaType;
  required?: boolean;
  minimum?: number;
  maximum?: number;
  maxLength?: number;
  selector?: string;
}

export type FieldSchema = FieldSchemaType | ExtendedFieldSchema;

export interface ExtractSchemaOptions {
  schema: Record<string, FieldSchema>;
  prompt?: never;
}

export interface ExtractPromptOptions {
  prompt: string;
  example?: Record<string, unknown>;
  schema?: never;
}

export type ExtractOptions = ExtractSchemaOptions | ExtractPromptOptions;

export interface FetchResult {
  content: string;
  content_type: string;
  fetched_at: string;
  url: string;
}

export interface ExtractResult {
  data: Record<string, unknown>;
  inferred_schema?: Record<string, string>;
  url: string;
  fetched_at: string;
  credits_used: number;
  confidence?: Record<string, string | null>;
}

export interface JobStatus {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  result?: ExtractResult;
  created_at?: string;
}

export interface DataskClientOptions {
  apiKey?: string;
  baseUrl?: string;
  timeout?: number;
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

const DEFAULT_BASE_URL = "https://api.datask.run";
const DEFAULT_TIMEOUT = 90_000;
const MAX_POLL_MS = 120_000;
const POLL_INTERVAL_MS = 2_000;

export class DataskClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly timeout: number;

  constructor(options: DataskClientOptions = {}) {
    const apiKey =
      options.apiKey ?? (typeof process !== "undefined" ? process.env.DATASK_API_KEY : undefined) ?? "";

    if (!apiKey) {
      throw new AuthenticationError(
        "API key required. Set DATASK_API_KEY env var or pass apiKey option."
      );
    }

    this.apiKey = apiKey;
    this.baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, "");
    this.timeout = options.timeout ?? DEFAULT_TIMEOUT;
  }

  private get headers(): Record<string, string> {
    return {
      Authorization: `Bearer ${this.apiKey}`,
      "Content-Type": "application/json",
    };
  }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    try {
      const resp = await fetch(`${this.baseUrl}${path}`, {
        ...init,
        headers: { ...this.headers, ...(init?.headers as Record<string, string>) },
        signal: controller.signal,
      });

      if (resp.ok) {
        return resp.json() as Promise<T>;
      }

      let body: Record<string, unknown> = {};
      try {
        body = await resp.json();
      } catch {}

      const msg = (body.message as string) ?? `HTTP ${resp.status}`;

      if (resp.status === 401) throw new AuthenticationError(msg);
      if (resp.status === 402)
        throw new QuotaExceededError(msg, body.upgrade_url as string | undefined);
      if (resp.status === 429)
        throw new RateLimitError(msg, (body.retry_after as number) ?? 60);

      throw new DataskError((body.error as string) ?? "unknown_error", msg, resp.status);
    } finally {
      clearTimeout(timer);
    }
  }

  /**
   * Layer 1 — Fetch clean Markdown content from any URL.
   * Includes Cloudflare bypass.
   */
  async fetch(url: string): Promise<string> {
    const result = await this.request<FetchResult>(
      `/v1/fetch?url=${encodeURIComponent(url)}`
    );
    return result.content;
  }

  /**
   * Layer 2/3 — Extract structured data from a URL.
   *
   * Layer 2: pass `schema` — CSS selector hints or type-only schema.
   * Layer 3: pass `prompt` — natural language description.
   */
  async extract(url: string, options: ExtractOptions): Promise<Record<string, unknown>> {
    const body: Record<string, unknown> = { url };

    if ("schema" in options && options.schema) {
      body.schema = options.schema;
    } else if ("prompt" in options && options.prompt) {
      body.prompt = options.prompt;
      if (options.example) {
        body.example = options.example;
      }
    }

    const result = await this.request<ExtractResult>("/v1/extract", {
      method: "POST",
      body: JSON.stringify(body),
    });

    return result.data;
  }

  /**
   * Extract with async mode — returns job_id immediately, then polls.
   */
  async extractAsync(
    url: string,
    options: ExtractOptions
  ): Promise<Record<string, unknown>> {
    const body: Record<string, unknown> = { url };

    if ("schema" in options && options.schema) {
      body.schema = options.schema;
    } else if ("prompt" in options && options.prompt) {
      body.prompt = options.prompt;
      if (options.example) body.example = options.example;
    }

    const resp = await this.request<{ job_id: string; status: string }>("/v1/extract", {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "X-Datask-Async": "true" },
    });

    return this.pollJob(resp.job_id);
  }

  /**
   * Poll an async job until completion.
   */
  async pollJob(jobId: string): Promise<Record<string, unknown>> {
    const deadline = Date.now() + MAX_POLL_MS;
    while (Date.now() < deadline) {
      const job = await this.request<JobStatus>(`/v1/jobs/${jobId}`);
      if (job.status === "completed") {
        return (job.result?.data ?? job.result ?? {}) as Record<string, unknown>;
      }
      if (job.status === "failed") {
        throw new DataskError("extraction_failed", `Job ${jobId} failed`, 500);
      }
      await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
    }
    throw new Error(`Job ${jobId} timed out after ${MAX_POLL_MS / 1000}s`);
  }
}
