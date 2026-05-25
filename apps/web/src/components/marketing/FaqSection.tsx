"use client";

import { useState } from "react";
import { clsx } from "clsx";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { Add01Icon, Cancel01Icon } from "@hugeicons/core-free-icons";

const FAQS = [
  {
    q: "How does Datask bypass Cloudflare Turnstile?",
    a: "We use Scrapling v0.4.6 — a Python library with native Turnstile challenge solving, TLS fingerprint spoofing, and browser fingerprint impersonation. It handles all Turnstile challenge types automatically. You don't configure anything.",
  },
  {
    q: "What's the difference between Layer 1, 2, and 3?",
    a: "Layer 1 (GET /v1/fetch) is free, no auth, returns clean Markdown. Layer 2 (POST /v1/extract + schema) requires an API key and returns structured JSON matching your schema. Layer 3 (POST /v1/extract + prompt) uses an LLM to infer the schema from plain English.",
  },
  {
    q: "How does billing work?",
    a: "Free tier: 500 req/month, no credit card. PAYG: $0.005/req billed monthly via Stripe. Commit plans are invoiced upfront. You're only charged for completed requests — failed requests don't count.",
  },
  {
    q: "Is my scraped content stored?",
    a: "No. Datask is stateless per request. Content is processed and returned in the same HTTP response — never stored beyond delivery. URL and response metadata (status, timing) are logged for billing and debugging.",
  },
  {
    q: "What about rate limits?",
    a: "Free tier: 2 concurrent, 10 req/min burst. PAYG: 10 concurrent, 60 req/min. All 429 responses include Retry-After and upgrade_url fields.",
  },
  {
    q: "Can I use Datask in a LangChain / CrewAI agent?",
    a: "Yes. A Python SDK (pip install datask-py) and MCP server are coming in Phase 2. For now, use the REST API directly — it's designed to be easy to wrap in an agent tool.",
  },
];

export function FaqSection() {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <section className="bg-canvas py-24 border-t border-hairline-soft">
      <div className="container-app max-w-[720px]">
        <p className="text-caption text-ink-muted uppercase tracking-widest mb-4">FAQ</p>
        <h2 className="text-display-lg text-ink mb-12">Common questions.</h2>

        <div className="divide-y divide-hairline-soft">
          {FAQS.map((faq, i) => (
            <div key={i} className="py-5">
              <button
                onClick={() => setOpen(open === i ? null : i)}
                className="w-full flex items-center justify-between gap-4 text-left"
              >
                <span className="text-body text-ink">{faq.q}</span>
                <Icon
                  icon={(open === i ? Cancel01Icon : Add01Icon) as IconProp}
                  size={18}
                  className={clsx("text-ink-muted shrink-0 transition-transform", open === i && "rotate-90")}
                />
              </button>
              {open === i && (
                <p className="text-body text-ink-muted mt-3 leading-relaxed">{faq.a}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
