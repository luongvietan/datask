"use client";

import { useEffect, useState, type FormEvent } from "react";
import { Button } from "@/components/ui/Button";

interface Props {
  targetUrl: string;
}

interface FetchResult {
  content: string;
  fetched_at: string;
  url: string;
}

const CODE_EXAMPLES = {
  curl: (url: string) =>
    `curl "https://api.datask.run/v1/fetch?url=${encodeURIComponent(url)}"`,
  python: (url: string) =>
    `import datask\n\nclient = datask.Client()\ncontent = client.fetch("${url}")\nprint(content)`,
  javascript: (url: string) =>
    `import { DataskClient } from "datask";\n\nconst client = new DataskClient();\nconst content = await client.fetch("${url}");\nconsole.log(content);`,
};

export function RunPageClient({ targetUrl }: Props) {
  const [result, setResult] = useState<FetchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [lang, setLang] = useState<keyof typeof CODE_EXAMPLES>("curl");
  const [nextUrl, setNextUrl] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setResult(null);
    setError(null);

    fetch(`/api/v1/fetch?url=${encodeURIComponent(targetUrl)}`)
      .then(async (res) => {
        if (cancelled) return;
        const text = await res.text();
        if (res.ok) {
          try { setResult(JSON.parse(text) as FetchResult); }
          catch { setError("Unexpected response from API."); }
        } else {
          try {
            const body = JSON.parse(text);
            setError(body.message ?? `HTTP ${res.status}`);
          } catch {
            setError(`HTTP ${res.status}`);
          }
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err.message ?? "Failed to reach Datask API.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [targetUrl]);

  function copyContent() {
    if (!result?.content) return;
    navigator.clipboard.writeText(result.content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  function handleNavigate(e: FormEvent) {
    e.preventDefault();
    const target = nextUrl.trim();
    if (!target) return;
    const full = /^https?:\/\//i.test(target) ? target : `https://${target}`;
    window.location.href = `/run?url=${encodeURIComponent(full)}`;
  }

  const codeSnippet = CODE_EXAMPLES[lang](targetUrl);

  return (
    <div className="min-h-screen bg-canvas">
      {/* Header */}
      <div className="border-b border-hairline px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3 min-w-0">
          <a href="/" className="text-body-sm font-bold text-ink shrink-0">
            Datask
          </a>
          <span className="text-ink-muted shrink-0">/</span>
          <span className="text-caption text-ink-muted font-mono truncate">
            {targetUrl}
          </span>
        </div>
        {result?.fetched_at && (
          <span className="text-micro text-ink-muted shrink-0 ml-4">
            Fetched {new Date(result.fetched_at).toLocaleTimeString()}
          </span>
        )}
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* Try another URL */}
        <form onSubmit={handleNavigate} className="flex gap-2">
          <div className="flex-1 bg-surface-1 rounded-xl p-1.5 flex items-center gap-2 border border-hairline focus-within:border-accent-blue/50 transition-colors">
            <span className="text-caption text-ink-muted px-3 shrink-0 select-none">datask.run/</span>
            <input
              type="url"
              value={nextUrl}
              onChange={(e) => setNextUrl(e.target.value)}
              placeholder="Try another URL…"
              className="flex-1 bg-transparent text-body-sm text-ink font-mono placeholder:text-ink-muted/50 outline-none min-w-0"
            />
          </div>
          <button
            type="submit"
            disabled={!nextUrl.trim()}
            className="btn-primary text-[13px] px-4 py-2 shrink-0 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Fetch →
          </button>
        </form>

        {/* Loading state */}
        {loading && (
          <div className="flex items-center gap-3 py-4">
            <span className="size-2 rounded-full bg-accent-blue animate-pulse shrink-0" />
            <span className="text-caption text-ink-muted">
              Fetching <span className="font-mono text-ink">{targetUrl}</span> — bypassing anti-bot…
            </span>
          </div>
        )}

        {/* Error state */}
        {!loading && error && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-6 space-y-3">
            <p className="text-body-sm text-red-400 font-medium">Fetch failed</p>
            <p className="text-caption text-ink-muted font-mono">{error}</p>
            <p className="text-caption text-ink-muted">
              The API may not be running, or this site is blocking requests.{" "}
              <a href="/register" className="text-accent-blue hover:underline">
                Get a free API key →
              </a>
            </p>
          </div>
        )}

        {/* Success + Content */}
        {!loading && result && (
          <>
            <div className="flex items-center gap-2">
              <span className="size-2 rounded-full bg-success-green shrink-0" />
              <span className="text-caption text-success-green">
                Successfully fetched — Cloudflare bypass active
              </span>
            </div>

            <div className="rounded-xl border border-hairline bg-surface-1">
              <div className="flex items-center justify-between px-4 py-3 border-b border-hairline">
                <span className="text-caption text-ink-muted">Content (Markdown)</span>
                <Button variant="ghost" size="sm" onClick={copyContent}>
                  {copied ? "Copied!" : "Copy"}
                </Button>
              </div>
              <pre className="p-4 text-caption text-ink font-mono overflow-auto max-h-[500px] whitespace-pre-wrap">
                {result.content}
              </pre>
            </div>
          </>
        )}

        {/* Code snippet — always shown */}
        {!loading && (
          <div className="rounded-xl border border-hairline bg-surface-1">
            <div className="px-4 py-3 border-b border-hairline flex items-center justify-between">
              <span className="text-caption text-ink-muted">Use in your code</span>
              <div className="flex gap-1">
                {(["curl", "python", "javascript"] as const).map((l) => (
                  <button
                    key={l}
                    onClick={() => setLang(l)}
                    className={`text-micro px-2 py-1 rounded-md transition-colors ${
                      lang === l ? "bg-surface-2 text-ink" : "text-ink-muted hover:text-ink"
                    }`}
                  >
                    {l}
                  </button>
                ))}
              </div>
            </div>
            <pre className="p-4 text-caption text-success-green font-mono overflow-auto">
              {codeSnippet}
            </pre>
            <div className="px-4 py-3 border-t border-hairline flex items-center justify-between flex-wrap gap-3">
              <span className="text-micro text-ink-muted">
                Want structured JSON?{" "}
                <a href="/docs" className="text-accent-blue hover:underline">
                  See Layer 2 & 3 docs →
                </a>
              </span>
              <a
                href="/register"
                className="text-caption text-ink bg-surface-2 hover:bg-surface-1 px-3 py-1.5 rounded-lg transition-colors border border-hairline"
              >
                Get free API key →
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
