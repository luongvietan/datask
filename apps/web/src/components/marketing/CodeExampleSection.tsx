"use client";

import { useState } from "react";
import { clsx } from "clsx";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { AlertCircleIcon, ValidationIcon } from "@hugeicons/core-free-icons";

const TABS = [
  {
    id: "python",
    label: "Python",
    code: `import datask

client = datask.Client(api_key="dtsk_live_...")

# Layer 1 — free fetch, no auth needed
content = client.fetch("https://cloudflare-site.com")

# Layer 2 — schema extraction
data = client.extract(
    "https://shop.example.com/product",
    schema={"price": "number", "title": "string"},
)
# → {"price": 49.99, "title": "Widget Pro"}

# Layer 3 — natural language
data = client.extract(
    "https://shop.example.com/product",
    prompt="Get me the price and title",
)
# → {"price": 49.99, "title": "Widget Pro"}`,
  },
  {
    id: "curl",
    label: "curl",
    code: `# Layer 1 — free, no auth
curl "https://api.datask.run/v1/fetch?url=https://cloudflare-site.com"

# Layer 2 — schema extraction
curl -X POST https://api.datask.run/v1/extract \\
  -H "Authorization: Bearer dtsk_live_..." \\
  -H "Content-Type: application/json" \\
  -d '{
    "url": "https://shop.example.com/product",
    "schema": {"price": "number", "title": "string"}
  }'

# Layer 3 — natural language prompt
curl -X POST https://api.datask.run/v1/extract \\
  -H "Authorization: Bearer dtsk_live_..." \\
  -H "Content-Type: application/json" \\
  -d '{
    "url": "https://shop.example.com/product",
    "prompt": "Get me the price and title"
  }'`,
  },
  {
    id: "firecrawl",
    label: "vs Firecrawl",
    isComparison: true,
    code: `// Firecrawl — fails on Cloudflare Turnstile
const result = await app.scrapeUrl("https://cloudflare-protected.com");
// → 403 Forbidden (bot detected)
// → Credit still consumed
// GitHub issue #2413: "still using credit on bot detection"

// Then you need a SECOND LLM call to extract data:
const extracted = await openai.chat.completions.create({
  messages: [{ role: "user", content: \`Extract price from: \${result.markdown}\` }]
});
// → {"price": 49.99}  (after 2 API calls + extra cost)`,
    codeB: `// Datask — native Turnstile bypass, structured in one call
const data = await fetch("https://api.datask.run/v1/extract", {
  method: "POST",
  headers: { "Authorization": "Bearer dtsk_live_..." },
  body: JSON.stringify({
    url: "https://cloudflare-protected.com",
    prompt: "Get me the price"
  })
});
// → {"price": 49.99}  ✓ one request, one cost, works`,
  },
];

export function CodeExampleSection() {
  const [active, setActive] = useState(0);
  const tab = TABS[active];

  return (
    <section className="bg-canvas py-24 border-t border-hairline-soft">
      <div className="container-app">
        <p className="text-caption text-ink-muted uppercase tracking-widest mb-4">Quick start</p>
        <h2 className="text-display-lg text-ink mb-4">
          From zero to data in 60 seconds.
        </h2>
        <p className="text-body-lg text-ink-muted mb-10 max-w-[480px]">
          No configuration. No headless browser setup. No proxy management.
        </p>

        {/* Tabs */}
        <div className="flex gap-1 mb-4 bg-surface-1 rounded-xl p-1 max-w-max">
          {TABS.map((t, i) => (
            <button
              key={t.id}
              onClick={() => setActive(i)}
              className={clsx(
                "px-4 py-2 rounded-lg text-caption font-medium transition-colors whitespace-nowrap",
                active === i
                  ? "bg-surface-2 text-ink"
                  : "text-ink-muted hover:text-ink",
                t.id === "firecrawl" && active === i && "text-[#F59E0B]",
                t.id === "firecrawl" && active !== i && "hover:text-[#F59E0B]"
              )}
            >
              {t.label}
            </button>
          ))}
        </div>

        {tab.isComparison ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="code-block border border-[#F59E0B]/20">
              <p className="text-caption text-[#F59E0B] mb-4 uppercase tracking-widest flex items-center gap-2">
                <Icon icon={AlertCircleIcon as IconProp} size={14} className="shrink-0" />
                Firecrawl
              </p>
              <pre className="text-[13px] font-mono text-ink-muted leading-relaxed whitespace-pre overflow-x-auto">
                <code>{tab.code}</code>
              </pre>
            </div>
            <div className="code-block border border-success-green/20">
              <p className="text-caption text-success-green mb-4 uppercase tracking-widest flex items-center gap-2">
                <Icon icon={ValidationIcon as IconProp} size={14} className="shrink-0" />
                Datask
              </p>
              <pre className="text-[13px] font-mono text-ink leading-relaxed whitespace-pre overflow-x-auto">
                <code>{tab.codeB}</code>
              </pre>
            </div>
          </div>
        ) : (
          <div className="code-block max-w-[720px]">
            <p className="text-caption text-ink-muted mb-4 uppercase tracking-widest">{tab.label}</p>
            <pre className="text-[13px] font-mono text-ink leading-relaxed whitespace-pre overflow-x-auto">
              <code>{tab.code}</code>
            </pre>
          </div>
        )}
      </div>
    </section>
  );
}
