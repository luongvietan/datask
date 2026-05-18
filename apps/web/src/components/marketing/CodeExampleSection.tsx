const EXAMPLES = {
  python: `import datask

client = datask.Client(api_key="dtsk_live_...")

# Layer 1 — free fetch (no auth needed)
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

  curl: `# Layer 1 — free, no auth
curl "https://api.datask.run/v1/fetch?url=https://cloudflare-site.com"

# Layer 2 — schema extraction
curl -X POST https://api.datask.run/v1/extract \\
  -H "Authorization: Bearer dtsk_live_..." \\
  -H "Content-Type: application/json" \\
  -d '{
    "url": "https://shop.example.com/product",
    "schema": {"price": "number", "title": "string"}
  }'`,
};

export function CodeExampleSection() {
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

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Python */}
          <div className="code-block">
            <p className="text-caption text-ink-muted mb-4 uppercase tracking-widest">Python</p>
            <pre className="text-[13px] font-mono text-ink leading-relaxed whitespace-pre overflow-x-auto">
              <code>{EXAMPLES.python}</code>
            </pre>
          </div>

          {/* curl */}
          <div className="code-block">
            <p className="text-caption text-ink-muted mb-4 uppercase tracking-widest">curl</p>
            <pre className="text-[13px] font-mono text-ink leading-relaxed whitespace-pre overflow-x-auto">
              <code>{EXAMPLES.curl}</code>
            </pre>
          </div>
        </div>
      </div>
    </section>
  );
}
