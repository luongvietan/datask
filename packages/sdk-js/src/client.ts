import type {
  DataskClientOptions,
  ExtractOptions,
  ExtractResult,
  FetchResult,
} from "./types";
import { DataskError } from "./types";

const DEFAULT_BASE_URL = "https://api.datask.run";
const DEFAULT_TIMEOUT = 60_000;

export class DataskClient {
  private readonly apiKey: string | undefined;
  private readonly baseUrl: string;
  private readonly timeout: number;

  constructor(options: DataskClientOptions = {}) {
    this.apiKey = options.apiKey;
    this.baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, "");
    this.timeout = options.timeout ?? DEFAULT_TIMEOUT;
  }

  /**
   * Layer 1 — Fetch clean Markdown content from any URL.
   * Free, no API key required.
   */
  async fetch(url: string): Promise<FetchResult> {
    const params = new URLSearchParams({ url });
    return this.request<FetchResult>(`/v1/fetch?${params}`);
  }

  /**
   * Layer 2/3 — Extract structured data from a URL.
   * Requires an API key.
   *
   * @param url    The URL to scrape.
   * @param options  schema (Layer 2) or prompt (Layer 3).
   */
  async extract<T = Record<string, unknown>>(
    url: string,
    options: ExtractOptions<T>
  ): Promise<ExtractResult<T>> {
    if (!this.apiKey) {
      throw new DataskError(
        "missing_api_key",
        "API key required for extract(). Create one at https://datask.run",
        401
      );
    }

    return this.request<ExtractResult<T>>("/v1/extract", {
      method: "POST",
      body: JSON.stringify({
        url,
        ...(options.schema ? { schema: options.schema } : {}),
        ...(options.prompt ? { prompt: options.prompt } : {}),
        ...(options.example ? { example: options.example } : {}),
      }),
    });
  }

  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    try {
      const res = await fetch(`${this.baseUrl}${path}`, {
        ...init,
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
          "User-Agent": "datask-js/0.1.0",
          ...(this.apiKey ? { Authorization: `Bearer ${this.apiKey}` } : {}),
          ...init.headers,
        },
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({})) as Record<string, unknown>;
        throw new DataskError(
          String(body.error ?? "unknown_error"),
          String(body.message ?? `HTTP ${res.status}`),
          res.status,
          typeof body.retry_after === "number" ? body.retry_after : undefined,
          typeof body.upgrade_url === "string" ? body.upgrade_url : undefined
        );
      }

      return res.json() as Promise<T>;
    } finally {
      clearTimeout(timer);
    }
  }
}
