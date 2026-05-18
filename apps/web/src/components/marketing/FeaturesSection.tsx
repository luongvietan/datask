import { Card } from "@/components/ui/Card";

const FEATURES = [
  {
    variant: "violet" as const,
    eyebrow: "Native bypass",
    title: "Cloudflare Turnstile? Solved.",
    body:
      "Scrapling engine solves all Turnstile challenge types — TLS fingerprint spoofing, browser fingerprint impersonation. >95% success rate vs ~40% for Firecrawl.",
    stat: ">95%",
    statLabel: "success rate on CF-protected sites",
  },
  {
    variant: "default" as const,
    eyebrow: "Layer 3",
    title: "Describe what you want in plain English.",
    body:
      'Send a URL and a prompt: "Get me the price and title." Get back structured JSON. No CSS selectors. No XPath. No schema files.',
    stat: "1 request",
    statLabel: "URL + prompt → JSON",
  },
  {
    variant: "magenta" as const,
    eyebrow: "Self-healing",
    title: "Scraper breaks when site changes? We fix it.",
    body:
      "Scrapling's adaptive element tracking learns when websites change layout. Scraper maintenance cost = $0. Coming as a contractual SLA in Phase 3.",
    stat: "$0",
    statLabel: "scraper maintenance cost",
  },
  {
    variant: "default" as const,
    eyebrow: "Pricing",
    title: "Pay per successful request — not per attempt.",
    body:
      "Free tier 500 req/month. PAYG $0.005/req. Commit 10K/month at $0.003/req. Cheaper per successful request than every competitor.",
    stat: "$0.005",
    statLabel: "per request — no fixed monthly seat",
  },
];

export function FeaturesSection() {
  return (
    <section className="bg-canvas py-24 border-t border-hairline-soft">
      <div className="container-app">
        <p className="text-caption text-ink-muted uppercase tracking-widest mb-4">Why Datask</p>
        <h2 className="text-display-lg text-ink mb-14 max-w-[600px]">
          Three things no competitor has simultaneously.
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {FEATURES.map((f) => (
            <Card key={f.title} variant={f.variant} className="flex flex-col gap-4">
              <p className="text-caption text-ink-muted uppercase tracking-widest">{f.eyebrow}</p>
              <h3 className="text-display-md text-ink">{f.title}</h3>
              <p className="text-body text-ink-muted leading-relaxed flex-1">{f.body}</p>
              <div className="pt-4 border-t border-hairline-soft">
                <span className="text-display-md text-ink">{f.stat}</span>
                <p className="text-caption text-ink-muted mt-1">{f.statLabel}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
