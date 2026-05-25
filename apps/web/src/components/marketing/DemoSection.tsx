"use client";

import { useState, type FormEvent } from "react";
import { clsx } from "clsx";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { GlobeIcon, CodeIcon, SparklesIcon, ArrowRight01Icon } from "@hugeicons/core-free-icons";

const LAYERS: {
  id: string;
  label: string;
  icon: IconProp;
  badge: string;
  placeholder: string;
  hint: string;
  response: {
    status: string;
    time: string;
    tag: string;
    tagColor: string;
    content: string;
    contentColor: string;
  };
}[] = [
  {
    id: "layer1",
    label: "Layer 1 — Fetch",
    icon: GlobeIcon as IconProp,
    badge: "Free · No auth",
    placeholder: "https://cloudflare-protected-site.com",
    hint: "Paste any URL — Cloudflare-protected or not. Layer 1 is free, no API key needed.",
    response: {
      status: "200 OK",
      time: "1.4s",
      tag: "Cloudflare bypass",
      tagColor: "text-success-green",
      content: `# Product Page — Example Corp

## Pricing

**Starter** — $29/month
- 10,000 API calls
- Standard support

**Pro** — $99/month
- Unlimited API calls
- Priority support
- Custom integrations`,
      contentColor: "text-[#86EFAC]",
    },
  },
  {
    id: "layer2",
    label: "Layer 2 — Schema",
    icon: CodeIcon as IconProp,
    badge: "API key required",
    placeholder: "https://shop.example.com/product/42",
    hint: "Add a JSON schema to get structured typed data back. Requires a free API key.",
    response: {
      status: "200 OK",
      time: "1.7s",
      tag: "Structured JSON",
      tagColor: "text-accent-blue",
      content: `{
  "price": 49.99,
  "currency": "USD",
  "title": "Widget Pro — 3-pack",
  "in_stock": true,
  "rating": 4.8,
  "review_count": 312
}`,
      contentColor: "text-[#93C5FD]",
    },
  },
  {
    id: "layer3",
    label: "Layer 3 — NL Prompt",
    icon: SparklesIcon as IconProp,
    badge: "Commit plan",
    placeholder: "https://shop.example.com/product/42",
    hint: 'Describe what you want in plain English: "Get price, title, and stock status." No schema needed.',
    response: {
      status: "200 OK",
      time: "2.1s",
      tag: "Natural Language",
      tagColor: "text-[#C084FC]",
      content: `// Prompt: "Get me the price, title, and stock status"

{
  "price": 49.99,
  "title": "Widget Pro — 3-pack",
  "in_stock": true
}`,
      contentColor: "text-[#C084FC]",
    },
  },
];

export function DemoSection() {
  const [active, setActive] = useState(0);
  const [url, setUrl] = useState("");
  const layer = LAYERS[active];

  function handleFetch(e: FormEvent) {
    e.preventDefault();
    const target = url.trim();
    if (!target) return;
    const full = /^https?:\/\//i.test(target) ? target : `https://${target}`;
    window.location.href = `/run?url=${encodeURIComponent(full)}`;
  }

  return (
    <section className="bg-canvas py-20 border-t border-hairline-soft">
      <div className="container-app">
        <p className="text-caption text-ink-muted mb-4 uppercase tracking-widest">Try it now</p>
        <h2 className="text-display-lg text-ink mb-10">
          Three ways to get data.
        </h2>

        {/* Layer tabs */}
        <div className="flex gap-1 mb-6 bg-surface-1 rounded-xl p-1 max-w-max">
          {LAYERS.map((l, i) => (
            <button
              key={l.id}
              onClick={() => setActive(i)}
              className={clsx(
                "flex items-center gap-2 px-4 py-2 rounded-lg text-caption font-medium transition-colors whitespace-nowrap",
                active === i
                  ? "bg-surface-2 text-ink"
                  : "text-ink-muted hover:text-ink"
              )}
            >
              <Icon icon={l.icon} size={13} className="shrink-0" />
              {l.label}
            </button>
          ))}
        </div>

        {/* Badge + hint */}
        <div className="flex items-start gap-3 mb-5 flex-wrap">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-pill bg-surface-1 border border-hairline text-[11px] text-ink-muted shrink-0">
            {layer.badge}
          </span>
          <p className="text-body text-ink-muted">{layer.hint}</p>
        </div>

        {/* Functional URL bar — only active for Layer 1 */}
        {active === 0 ? (
          <form onSubmit={handleFetch} className="max-w-[680px] mb-4">
            <div className="bg-surface-1 rounded-xl p-1.5 flex items-center gap-2 border border-hairline focus-within:border-accent-blue/50 transition-colors">
              <span className="text-caption text-ink-muted px-3 shrink-0 select-none">datask.run/</span>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder={layer.placeholder}
                className="flex-1 bg-transparent text-body-sm text-ink font-mono placeholder:text-ink-muted/50 outline-none min-w-0"
              />
              <button
                type="submit"
                disabled={!url.trim()}
                className="btn-primary text-[13px] px-4 py-2 shrink-0 disabled:opacity-40 disabled:cursor-not-allowed inline-flex items-center gap-1.5"
              >
                Fetch
                <Icon icon={ArrowRight01Icon as IconProp} size={14} />
              </button>
            </div>
            <p className="text-[11px] text-ink-muted mt-2 pl-1">
              Opens the result in a new page. Free, no signup needed.
            </p>
          </form>
        ) : (
          /* Layers 2 & 3 — static preview, CTA to sign up */
          <div className="bg-surface-1 rounded-xl p-1.5 flex items-center gap-2 max-w-[680px] mb-4 border border-hairline opacity-60 cursor-not-allowed">
            <span className="text-caption text-ink-muted px-3 shrink-0">POST /v1/extract</span>
            <div className="flex-1 bg-surface-2 rounded-lg px-4 py-2.5 overflow-hidden">
              <code className="text-body-sm text-ink font-mono truncate block">{layer.placeholder}</code>
            </div>
            <a
              href="/register"
              className="btn-primary text-[13px] px-4 py-2 shrink-0 inline-flex items-center gap-1.5"
              onClick={(e) => e.stopPropagation()}
            >
              Get API key
              <Icon icon={ArrowRight01Icon as IconProp} size={14} />
            </a>
          </div>
        )}

        {/* Output preview */}
        <div className="code-block max-w-[680px]">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-success-green" />
            <span className={clsx("text-caption", layer.response.tagColor)}>
              {layer.response.status} · {layer.response.time} · {layer.response.tag}
            </span>
          </div>
          <pre className={clsx("text-[13px] leading-relaxed overflow-x-auto whitespace-pre-wrap", layer.response.contentColor)}>
            {layer.response.content}
          </pre>
        </div>

        <p className="text-caption text-ink-muted mt-5">
          All layers bypass Cloudflare Turnstile — sites Firecrawl, Jina, and curl can&apos;t access.
          <a href="/docs#cloudflare" className="text-accent-blue hover:underline ml-1">
            How it works →
          </a>
        </p>
      </div>
    </section>
  );
}
