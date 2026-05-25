"use client";

import { useState, type FormEvent } from "react";
import { clsx } from "clsx";
import { useSessionKey } from "@/hooks/useSessionKey";

type Layer = "fetch" | "schema" | "prompt";

interface RunResult {
  ok: boolean;
  status: number;
  data: unknown;
  elapsed: number;
}

const LAYER_META: Record<Layer, { label: string; badge: string; desc: string }> = {
  fetch: {
    label: "Layer 1 — Fetch",
    badge: "Free",
    desc: "Returns clean Markdown. No schema, no prompt needed.",
  },
  schema: {
    label: "Layer 2 — Schema",
    badge: "1 credit",
    desc: 'Define exactly which fields to extract as a JSON schema, e.g. {"price": "number", "title": "string"}.',
  },
  prompt: {
    label: "Layer 3 — NL Prompt",
    badge: "2 credits",
    desc: "Describe what you want in plain English, e.g. \"Get the product title, price, and whether it is in stock.\"",
  },
};

export function PlaygroundClient() {
  const { data: sk } = useSessionKey();
  const sessionKey = sk?.session_key ?? "";

  const [layer, setLayer] = useState<Layer>("fetch");
  const [url, setUrl] = useState("");
  const [schema, setSchema] = useState('{"title": "string", "price": "number"}');
  const [prompt, setPrompt] = useState("Get the product title and price.");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);

  async function handleRun(e: FormEvent) {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setResult(null);

    const t0 = performance.now();

    try {
      let res: Response;

      if (layer === "fetch") {
        res = await fetch(`/api/v1/fetch?url=${encodeURIComponent(url.trim())}`, {
          headers: sessionKey ? { Authorization: `Bearer ${sessionKey}` } : {},
        });
      } else {
        let body: Record<string, unknown> = { url: url.trim() };
        if (layer === "schema") {
          try {
            body.schema = JSON.parse(schema);
          } catch {
            setResult({ ok: false, status: 0, data: { error: "Invalid JSON schema" }, elapsed: 0 });
            setLoading(false);
            return;
          }
        } else {
          body.prompt = prompt.trim();
        }
        res = await fetch("/api/v1/extract", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(sessionKey ? { Authorization: `Bearer ${sessionKey}` } : {}),
          },
          body: JSON.stringify(body),
        });
      }

      const elapsed = Math.round(performance.now() - t0);
      const text = await res.text();
      let data: unknown;
      try { data = JSON.parse(text); } catch { data = { raw: text }; }
      setResult({ ok: res.ok, status: res.status, data, elapsed });
    } catch (err: unknown) {
      const elapsed = Math.round(performance.now() - t0);
      const message = err instanceof Error ? err.message : "Request failed";
      setResult({ ok: false, status: 0, data: { error: message }, elapsed });
    } finally {
      setLoading(false);
    }
  }

  const meta = LAYER_META[layer];

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div>
        <h1 className="text-display-md text-ink">Playground</h1>
        <p className="text-body text-ink-muted mt-1">
          Test the API live — requests count against your quota.
        </p>
      </div>

      {/* Layer tabs */}
      <div className="flex gap-1 bg-surface-1 rounded-xl p-1 max-w-max">
        {(["fetch", "schema", "prompt"] as Layer[]).map((l) => (
          <button
            key={l}
            onClick={() => { setLayer(l); setResult(null); }}
            className={clsx(
              "px-4 py-2 rounded-lg text-caption font-medium transition-colors whitespace-nowrap",
              layer === l ? "bg-surface-2 text-ink" : "text-ink-muted hover:text-ink"
            )}
          >
            {LAYER_META[l].label}
          </button>
        ))}
      </div>

      {/* Request form */}
      <form onSubmit={handleRun} className="space-y-4 bg-surface-1 rounded-xl p-5 border border-hairline">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-surface-2 border border-hairline text-[11px] text-ink-muted">
            {meta.badge}
          </span>
          <p className="text-caption text-ink-muted">{meta.desc}</p>
        </div>

        {/* URL */}
        <div>
          <label className="text-caption text-ink-muted block mb-1.5">URL</label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/product"
            required
            className="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2.5 text-body-sm text-ink font-mono placeholder:text-ink-muted/50 outline-none focus:border-accent-blue/50 transition-colors"
          />
        </div>

        {/* Layer 2: schema */}
        {layer === "schema" && (
          <div>
            <label className="text-caption text-ink-muted block mb-1.5">
              JSON Schema
            </label>
            <textarea
              value={schema}
              onChange={(e) => setSchema(e.target.value)}
              rows={4}
              spellCheck={false}
              className="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2.5 text-body-sm text-ink font-mono placeholder:text-ink-muted/50 outline-none focus:border-accent-blue/50 transition-colors resize-y"
            />
          </div>
        )}

        {/* Layer 3: prompt */}
        {layer === "prompt" && (
          <div>
            <label className="text-caption text-ink-muted block mb-1.5">
              Natural Language Prompt
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
              className="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2.5 text-body-sm text-ink placeholder:text-ink-muted/50 outline-none focus:border-accent-blue/50 transition-colors resize-y"
            />
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !url.trim() || !sessionKey}
          className="btn-primary px-5 py-2 text-body-sm disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <span className="size-2 rounded-full bg-white/60 animate-pulse" />
              Running…
            </>
          ) : (
            "Run →"
          )}
        </button>

        {!sessionKey && (
          <p className="text-caption text-ink-muted">
            Loading session…
          </p>
        )}
      </form>

      {/* Result */}
      {result && (
        <div className="bg-surface-1 rounded-xl border border-hairline overflow-hidden">
          {/* Status bar */}
          <div className={clsx(
            "px-4 py-3 border-b border-hairline flex items-center justify-between",
            result.ok ? "bg-success-green/5" : "bg-red-500/5"
          )}>
            <div className="flex items-center gap-2">
              <span className={clsx(
                "size-2 rounded-full shrink-0",
                result.ok ? "bg-success-green" : "bg-red-500"
              )} />
              <span className={clsx("text-caption font-medium", result.ok ? "text-success-green" : "text-red-400")}>
                {result.ok ? "Success" : "Failed"}
                {result.status > 0 && ` · HTTP ${result.status}`}
              </span>
            </div>
            <span className="text-caption text-ink-muted">{result.elapsed}ms</span>
          </div>

          {/* Body */}
          <pre className="p-4 text-[13px] font-mono text-ink leading-relaxed overflow-auto max-h-[480px] whitespace-pre-wrap">
            {JSON.stringify(result.data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
