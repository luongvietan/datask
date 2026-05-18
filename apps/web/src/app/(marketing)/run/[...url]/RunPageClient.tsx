"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";

interface Props {
  targetUrl: string;
  content: string | null;
  fetchError: string | null;
  fetchedAt: string | null;
}

const CODE_EXAMPLES = {
  curl: (url: string) =>
    `curl "https://api.datask.run/v1/fetch?url=${encodeURIComponent(url)}"`,
  python: (url: string) =>
    `import datask\n\nclient = datask.Client()\ncontent = client.fetch("${url}")\nprint(content)`,
  javascript: (url: string) =>
    `import { DataskClient } from "datask";\n\nconst client = new DataskClient();\nconst content = await client.fetch("${url}");\nconsole.log(content);`,
};

export function RunPageClient({ targetUrl, content, fetchError, fetchedAt }: Props) {
  const [copied, setCopied] = useState(false);
  const [lang, setLang] = useState<keyof typeof CODE_EXAMPLES>("curl");

  function copyContent() {
    if (!content) return;
    navigator.clipboard.writeText(content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  const codeSnippet = CODE_EXAMPLES[lang](targetUrl);

  return (
    <div className="min-h-screen bg-canvas">
      {/* Header */}
      <div className="border-b border-border/50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <a href="/" className="text-body-sm font-bold text-ink">
            Datask
          </a>
          <span className="text-ink-muted">/</span>
          <span className="text-caption text-ink-muted font-mono truncate max-w-[400px]">
            {targetUrl}
          </span>
        </div>
        {fetchedAt && (
          <span className="text-micro text-ink-muted">
            Fetched {new Date(fetchedAt).toLocaleTimeString()}
          </span>
        )}
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">
        {/* Status / Error */}
        {fetchError ? (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-6">
            <p className="text-body-sm text-red-400 font-medium mb-1">Fetch failed</p>
            <p className="text-caption text-ink-muted">{fetchError}</p>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <span className="size-2 rounded-full bg-green-400" />
            <span className="text-caption text-green-400">
              Successfully fetched — including Cloudflare-protected sites
            </span>
          </div>
        )}

        {/* Content */}
        {content && (
          <div className="rounded-xl border border-border bg-surface-1">
            <div className="flex items-center justify-between px-4 py-3 border-b border-border">
              <span className="text-caption text-ink-muted">Content (Markdown)</span>
              <Button variant="ghost" size="sm" onClick={copyContent}>
                {copied ? "Copied!" : "Copy"}
              </Button>
            </div>
            <pre className="p-4 text-caption text-ink font-mono overflow-auto max-h-[500px] whitespace-pre-wrap">
              {content}
            </pre>
          </div>
        )}

        {/* "Use in code" section */}
        <div className="rounded-xl border border-border bg-surface-1">
          <div className="px-4 py-3 border-b border-border flex items-center justify-between">
            <span className="text-caption text-ink-muted">Use this in your code</span>
            <div className="flex gap-1">
              {(["curl", "python", "javascript"] as const).map((l) => (
                <button
                  key={l}
                  onClick={() => setLang(l)}
                  className={`text-micro px-2 py-1 rounded-md transition-colors ${
                    lang === l
                      ? "bg-surface-2 text-ink"
                      : "text-ink-muted hover:text-ink"
                  }`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>
          <pre className="p-4 text-caption text-green-400 font-mono overflow-auto">
            {codeSnippet}
          </pre>
          <div className="px-4 py-3 border-t border-border flex items-center justify-between">
            <span className="text-micro text-ink-muted">
              Want structured JSON?{" "}
              <a href="/docs" className="text-ink underline underline-offset-2">
                See API docs →
              </a>
            </span>
            <a
              href="/register"
              className="text-caption text-ink bg-surface-2 hover:bg-surface-1 px-3 py-1.5 rounded-lg transition-colors"
            >
              Get free API key
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
