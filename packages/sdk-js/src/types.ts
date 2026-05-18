export interface DataskClientOptions {
  /** Your Datask API key (dtsk_live_...). Not required for Layer 1 fetch(). */
  apiKey?: string;
  /** Override the API base URL. Default: https://api.datask.run */
  baseUrl?: string;
  /** Request timeout in milliseconds. Default: 60_000 */
  timeout?: number;
}

export interface FetchResult {
  content: string;
  content_type: "markdown" | "text";
  url: string;
  fetched_at: string;
}

export interface ExtractResult<T = Record<string, unknown>> {
  data: T;
  inferred_schema?: Record<string, string>;  // Layer 3 only
  url: string;
  fetched_at: string;
  credits_used: number;
}

export interface ExtractOptions<T = Record<string, unknown>> {
  /** JSON schema for Layer 2 structured extraction */
  schema?: Record<string, string>;
  /** Natural language description for Layer 3 extraction */
  prompt?: string;
  /** Optional example output to guide Layer 3 format */
  example?: T;
}

export class DataskError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status: number,
    public readonly retryAfter?: number,
    public readonly upgradeUrl?: string
  ) {
    super(message);
    this.name = "DataskError";
  }
}
