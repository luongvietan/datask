import type { Metadata } from "next";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Icon, type IconProp } from "@/components/ui/Icon";
import {
  ArrowRight01Icon,
  ValidationIcon,
  GlobeIcon,
} from "@hugeicons/core-free-icons";
import { CtaSection } from "@/components/marketing/CtaSection";

export const metadata: Metadata = {
  title: "Turnstile Benchmark 2026: Datask vs Firecrawl",
  description:
    "Head-to-head benchmark of Datask vs Firecrawl on 30 Cloudflare Turnstile-protected sites. Datask achieves 93.3% success rate vs Firecrawl's 30%.",
  openGraph: {
    title: "Turnstile Benchmark 2026: Datask vs Firecrawl",
    description:
      "We tested Datask and Firecrawl on 30 Turnstile-protected sites. Here are the honest results.",
    type: "article",
  },
};

const GITHUB_BENCHMARK_URL =
  "https://github.com/datask-run/datask/tree/main/benchmarks/turnstile-2026";

const RESULTS = {
  datask: {
    total: 30,
    success: 28,
    successRate: 93.3,
    latencyP50: 2738,
    latencyP95: 3337,
    latencyMean: 2473,
    avgContentLength: 13773,
    turnstileSuccess: 95.0,
    ecommerceSuccess: 90.0,
    costPer1k: 1.0,
    totalTime: 43.9,
  },
  firecrawl: {
    total: 30,
    success: 9,
    successRate: 30.0,
    latencyP50: 1650,
    latencyP95: 2240,
    latencyMean: 1599,
    avgContentLength: 6703,
    turnstileSuccess: 25.0,
    ecommerceSuccess: 40.0,
    costPer1k: 1.0,
    totalTime: 113.3,
  },
} as const;

function MetricRow({
  label,
  dataskValue,
  firecrawlValue,
  winner,
}: {
  label: string;
  dataskValue: string;
  firecrawlValue: string;
  winner: "datask" | "firecrawl" | "tie";
}) {
  return (
    <tr className="border-b border-hairline-soft">
      <td className="py-3 text-ink-muted text-caption">{label}</td>
      <td
        className={`py-3 text-center text-body-sm font-medium ${
          winner === "datask" ? "text-accent-blue" : "text-ink-muted"
        }`}
      >
        {dataskValue}
      </td>
      <td
        className={`py-3 text-center text-body-sm font-medium ${
          winner === "firecrawl" ? "text-accent-blue" : "text-ink-muted"
        }`}
      >
        {firecrawlValue}
      </td>
    </tr>
  );
}

export default function BenchmarkBlogPage() {
  return (
    <>
      <article>
        {/* Hero */}
        <section className="bg-canvas pt-20 pb-12 lg:pt-28 lg:pb-16">
          <div className="container-app">
            <div className="flex flex-wrap items-center gap-3 mb-6">
              <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-pill bg-surface-1 text-caption text-ink-muted border border-hairline">
                Benchmark
              </span>
              <span className="text-caption text-ink-muted">June 2026</span>
            </div>

            <h1 className="text-display-lg text-ink mb-6 max-w-[720px]">
              Turnstile Benchmark 2026:
              <br />
              <span className="text-accent-blue">Datask vs Firecrawl</span>
            </h1>

            <p className="text-body-lg text-ink-muted max-w-[600px] mb-8">
              We ran both APIs against 30 Cloudflare Turnstile-protected sites.
              Here are the honest, reproducible results.
            </p>

            <div className="flex flex-wrap items-center gap-3">
              <a href={GITHUB_BENCHMARK_URL} target="_blank" rel="noopener noreferrer">
                <Button variant="secondary" size="lg">
                  <span className="inline-flex items-center gap-2">
                    <Icon icon={GlobeIcon as IconProp} size={16} />
                    View on GitHub
                  </span>
                </Button>
              </a>
              <Link href="/register">
                <Button variant="primary" size="lg">
                  <span className="inline-flex items-center gap-2">
                    Try Datask free
                    <Icon icon={ArrowRight01Icon as IconProp} size={16} />
                  </span>
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* TL;DR Results */}
        <section className="bg-canvas py-16 border-t border-hairline-soft">
          <div className="container-app">
            <p className="text-caption text-ink-muted uppercase tracking-widest mb-4">
              TL;DR
            </p>
            <h2 className="text-display-md text-ink mb-10">
              3&times; higher success rate on protected sites.
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-12">
              <div className="bg-surface-1 rounded-xl p-6 border border-hairline">
                <p className="text-caption text-ink-muted mb-2">Datask success</p>
                <p className="text-display-md text-accent-blue">
                  {RESULTS.datask.successRate}%
                </p>
                <p className="text-caption text-ink-muted mt-1">
                  {RESULTS.datask.success}/{RESULTS.datask.total} sites
                </p>
              </div>
              <div className="bg-surface-1 rounded-xl p-6 border border-hairline">
                <p className="text-caption text-ink-muted mb-2">
                  Firecrawl success
                </p>
                <p className="text-display-md text-ink-muted">
                  {RESULTS.firecrawl.successRate}%
                </p>
                <p className="text-caption text-ink-muted mt-1">
                  {RESULTS.firecrawl.success}/{RESULTS.firecrawl.total} sites
                </p>
              </div>
              <div className="bg-surface-1 rounded-xl p-6 border border-hairline">
                <p className="text-caption text-ink-muted mb-2">
                  Turnstile-only (Datask)
                </p>
                <p className="text-display-md text-accent-blue">
                  {RESULTS.datask.turnstileSuccess}%
                </p>
                <p className="text-caption text-ink-muted mt-1">
                  19/20 CF-protected sites
                </p>
              </div>
            </div>

            {/* Results table */}
            <div className="overflow-x-auto">
              <table className="w-full text-body-sm min-w-[480px]">
                <thead>
                  <tr className="border-b border-hairline">
                    <th className="text-left pb-4 font-medium text-ink-muted w-[200px]">
                      Metric
                    </th>
                    <th className="text-center pb-4 font-medium text-accent-blue">
                      Datask
                    </th>
                    <th className="text-center pb-4 font-medium text-ink-muted">
                      Firecrawl
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <MetricRow
                    label="Success rate"
                    dataskValue={`${RESULTS.datask.successRate}%`}
                    firecrawlValue={`${RESULTS.firecrawl.successRate}%`}
                    winner="datask"
                  />
                  <MetricRow
                    label="Successful fetches"
                    dataskValue={`${RESULTS.datask.success}/${RESULTS.datask.total}`}
                    firecrawlValue={`${RESULTS.firecrawl.success}/${RESULTS.firecrawl.total}`}
                    winner="datask"
                  />
                  <MetricRow
                    label="Latency p50"
                    dataskValue={`${RESULTS.datask.latencyP50.toLocaleString()} ms`}
                    firecrawlValue={`${RESULTS.firecrawl.latencyP50.toLocaleString()} ms`}
                    winner="firecrawl"
                  />
                  <MetricRow
                    label="Latency p95"
                    dataskValue={`${RESULTS.datask.latencyP95.toLocaleString()} ms`}
                    firecrawlValue={`${RESULTS.firecrawl.latencyP95.toLocaleString()} ms`}
                    winner="firecrawl"
                  />
                  <MetricRow
                    label="Avg content length"
                    dataskValue={`${RESULTS.datask.avgContentLength.toLocaleString()} chars`}
                    firecrawlValue={`${RESULTS.firecrawl.avgContentLength.toLocaleString()} chars`}
                    winner="datask"
                  />
                  <MetricRow
                    label="Cost per 1K success"
                    dataskValue={`$${RESULTS.datask.costPer1k.toFixed(2)}`}
                    firecrawlValue={`$${RESULTS.firecrawl.costPer1k.toFixed(2)}`}
                    winner="tie"
                  />
                  <MetricRow
                    label="Turnstile sites"
                    dataskValue={`${RESULTS.datask.turnstileSuccess}% (19/20)`}
                    firecrawlValue={`${RESULTS.firecrawl.turnstileSuccess}% (5/20)`}
                    winner="datask"
                  />
                  <MetricRow
                    label="E-commerce sites"
                    dataskValue={`${RESULTS.datask.ecommerceSuccess}% (9/10)`}
                    firecrawlValue={`${RESULTS.firecrawl.ecommerceSuccess}% (4/10)`}
                    winner="datask"
                  />
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Methodology */}
        <section className="bg-canvas py-16 border-t border-hairline-soft">
          <div className="container-app max-w-[720px]">
            <p className="text-caption text-ink-muted uppercase tracking-widest mb-4">
              Methodology
            </p>
            <h2 className="text-display-md text-ink mb-8">How we tested</h2>

            <div className="space-y-8 text-body text-ink-muted leading-relaxed">
              <div>
                <h3 className="text-body-lg font-medium text-ink mb-3">
                  Site selection
                </h3>
                <p>
                  30 sites split into two categories:{" "}
                  <strong className="text-ink">20 Turnstile-protected</strong>{" "}
                  pages (Cloudflare demos, login pages from GitHub, Shopify,
                  Notion, Figma, Vercel, etc.) and{" "}
                  <strong className="text-ink">10 e-commerce</strong> sites
                  (Amazon, eBay, Etsy, Walmart, BestBuy, Target, Newegg,
                  AliExpress, Zalando, Lazada).
                </p>
              </div>

              <div>
                <h3 className="text-body-lg font-medium text-ink mb-3">
                  Success criteria
                </h3>
                <p>
                  A request counts as successful when it returns{" "}
                  <strong className="text-ink">HTTP 200</strong> with{" "}
                  <strong className="text-ink">
                    more than 500 characters
                  </strong>{" "}
                  of Markdown content. This filters out CAPTCHA challenge pages
                  that return short HTML blobs instead of real page content.
                </p>
              </div>

              <div>
                <h3 className="text-body-lg font-medium text-ink mb-3">
                  Configuration
                </h3>
                <p>
                  Both APIs were tested with identical settings: concurrency of
                  3, 2 retries per request, 60-second timeout, and rate limit
                  respect via <code className="text-accent-blue">Retry-After</code>{" "}
                  headers on 429 responses.
                </p>
              </div>

              <div>
                <h3 className="text-body-lg font-medium text-ink mb-3">
                  API endpoints
                </h3>
                <ul className="space-y-2">
                  <li>
                    <strong className="text-ink">Datask:</strong>{" "}
                    <code className="text-accent-blue">
                      GET /v1/fetch?url=&lt;url&gt;
                    </code>
                  </li>
                  <li>
                    <strong className="text-ink">Firecrawl:</strong>{" "}
                    <code className="text-accent-blue">
                      POST /v1/scrape
                    </code>{" "}
                    with <code className="text-accent-blue">{`{ "formats": ["markdown"] }`}</code>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Why Datask is slower */}
        <section className="bg-canvas py-16 border-t border-hairline-soft">
          <div className="container-app max-w-[720px]">
            <p className="text-caption text-ink-muted uppercase tracking-widest mb-4">
              Interpretation
            </p>
            <h2 className="text-display-md text-ink mb-8">
              Why is Datask slower?
            </h2>

            <div className="space-y-6 text-body text-ink-muted leading-relaxed">
              <p>
                Datask uses a headless browser with anti-bot evasion to solve
                Turnstile challenges. This adds latency compared to simple HTTP
                fetches — but the trade-off is a{" "}
                <strong className="text-ink">
                  significantly higher success rate
                </strong>{" "}
                on protected sites.
              </p>
              <p>
                Firecrawl&apos;s faster response times often come from returning
                early when encountering anti-bot challenges. The response is
                fast, but it frequently contains only the challenge HTML — not
                the actual page content. That&apos;s why the content length
                differs so dramatically (
                <strong className="text-ink">
                  13,773 vs 6,703 characters
                </strong>
                ).
              </p>
              <p>
                In short: <strong className="text-ink">speed is easy, success is hard</strong>.
                We optimize for getting you the actual data.
              </p>
            </div>
          </div>
        </section>

        {/* Honest reporting */}
        <section className="bg-canvas py-16 border-t border-hairline-soft">
          <div className="container-app max-w-[720px]">
            <p className="text-caption text-ink-muted uppercase tracking-widest mb-4">
              Transparency
            </p>
            <h2 className="text-display-md text-ink mb-8">
              Honest reporting policy
            </h2>

            <div className="space-y-6 text-body text-ink-muted leading-relaxed">
              <p>
                If benchmark numbers fall below marketing claims, we:
              </p>
              <ul className="space-y-3">
                {[
                  "Publish honest numbers — no cherry-picking",
                  "Document methodology fully so anyone can reproduce",
                  "Focus on methodology quality, not spinning results",
                  "Encourage independent verification",
                ].map((item) => (
                  <li key={item} className="flex items-start gap-3">
                    <span className="mt-1 shrink-0">
                      <Icon
                        icon={ValidationIcon as IconProp}
                        size={16}
                        className="text-success-green"
                      />
                    </span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
              <p>
                All benchmark scripts, site lists, and results are open source.
                Run them yourself with your own API keys.
              </p>
            </div>
          </div>
        </section>

        {/* Limitations */}
        <section className="bg-canvas py-16 border-t border-hairline-soft">
          <div className="container-app max-w-[720px]">
            <p className="text-caption text-ink-muted uppercase tracking-widest mb-4">
              Caveats
            </p>
            <h2 className="text-display-md text-ink mb-8">Limitations</h2>

            <div className="space-y-4">
              {[
                {
                  title: "Site availability changes",
                  text: "Websites update anti-bot configs frequently. Past results may not predict future performance.",
                },
                {
                  title: "Geographic bias",
                  text: "Benchmarks run from a single location. Latency varies by region.",
                },
                {
                  title: "Temporal bias",
                  text: "Sequential runs mean later sites see different server loads than earlier ones.",
                },
                {
                  title: "API version dependency",
                  text: "Results depend on the API versions available at the time of the run.",
                },
              ].map(({ title, text }) => (
                <div
                  key={title}
                  className="bg-surface-1 rounded-xl p-5 border border-hairline"
                >
                  <p className="text-body font-medium text-ink mb-1">{title}</p>
                  <p className="text-caption text-ink-muted leading-relaxed">
                    {text}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Reproduce */}
        <section className="bg-canvas py-16 border-t border-hairline-soft">
          <div className="container-app max-w-[720px]">
            <p className="text-caption text-ink-muted uppercase tracking-widest mb-4">
              Reproduce
            </p>
            <h2 className="text-display-md text-ink mb-8">Run it yourself</h2>

            <div className="code-block">
              <pre className="text-ink-muted">
{`# 1. Clone the repo
git clone https://github.com/datask-run/datask.git
cd datask

# 2. Install dependencies
uv sync --all-packages --dev

# 3. Set API keys
export DATASK_API_KEY="dtsk_live_..."
export FIRECRAWL_API_KEY="fc-..."

# 4. Run benchmarks
uv run python benchmarks/turnstile-2026/run_datask.py
uv run python benchmarks/turnstile-2026/run_firecrawl.py

# 5. Compare results
uv run python benchmarks/turnstile-2026/compare.py`}
              </pre>
            </div>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <a
                href={GITHUB_BENCHMARK_URL}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="secondary" size="lg">
                  <span className="inline-flex items-center gap-2">
                    <Icon icon={GlobeIcon as IconProp} size={16} />
                    Full benchmark repo
                  </span>
                </Button>
              </a>
            </div>
          </div>
        </section>
      </article>

      <CtaSection />
    </>
  );
}
