export function DemoSection() {
  return (
    <section className="bg-canvas py-20 border-t border-hairline-soft">
      <div className="container-app">
        <p className="text-caption text-ink-muted mb-4 uppercase tracking-widest">Layer 1 — Try it now</p>
        <h2 className="text-display-lg text-ink mb-10">
          Just paste a URL.
        </h2>

        {/* URL bar demo */}
        <div className="bg-surface-1 rounded-xl p-1.5 flex items-center gap-2 max-w-[680px] mb-4 border border-hairline">
          <span className="text-caption text-ink-muted px-3 shrink-0">datask.run/</span>
          <div className="flex-1 bg-surface-2 rounded-lg px-4 py-2.5">
            <code className="text-body-sm text-ink font-mono">
              https://cloudflare-protected.example.com
            </code>
          </div>
          <button className="btn-primary text-[13px] px-4 py-2 shrink-0">Fetch →</button>
        </div>

        {/* Output preview */}
        <div className="code-block max-w-[680px]">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-success-green" />
            <span className="text-caption text-ink-muted">200 OK · 1.4s · Cloudflare bypass</span>
          </div>
          <pre className="text-[#86EFAC] text-[13px] leading-relaxed overflow-x-auto whitespace-pre-wrap">
{`# Product Page — Example Corp

## Pricing

**Starter** — $29/month
- 10,000 API calls
- Standard support

**Pro** — $99/month  
- Unlimited API calls
- Priority support
- Custom integrations`}
          </pre>
        </div>

        <p className="text-caption text-ink-muted mt-5">
          Works on sites Firecrawl, Jina, and curl can&apos;t access.
          <a href="/docs#cloudflare" className="text-accent-blue hover:underline ml-1">
            How it works →
          </a>
        </p>
      </div>
    </section>
  );
}
