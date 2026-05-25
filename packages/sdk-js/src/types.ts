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

export interface ValidationErrorItem {
  field: string;
  code: "type_mismatch" | "missing_required" | "constraint_violation";
  message: string;
}

export interface ValidationWarningItem {
  field: string;
  code: "missing_optional";
  message: string;
}

export interface ValidationBlock {
  valid: boolean | null;
  errors: ValidationErrorItem[];
  warnings: ValidationWarningItem[];
}

export interface ExtractResult<T = Record<string, unknown>> {
  data: T;
  /** Layer 2 output validation; omitted for Layer 3 */
  validation?: ValidationBlock;
  inferred_schema?: Record<string, string>;  // Layer 3 only
  confidence?: Record<string, string | null>;
  meta?: {
    request_id: string;
    layer?: number;
    latency_ms?: number;
    model?: string;
    fetch_strategy?: string;
    cache_hit?: boolean;
  };
  url: string;
  fetched_at: string;
  credits_used: number;
}

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

export interface ExtractOptions<T = Record<string, unknown>> {
  /** JSON schema for Layer 2 structured extraction */
  schema?: Record<string, FieldSchema>;
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
