import Link from "next/link";
import { Button } from "@/components/ui/Button";

export function HeroSection() {
  return (
    <section className="bg-canvas pt-24 pb-20 lg:pt-32 lg:pb-28">
      <div className="container-app">
        {/* Eyebrow */}
        <div className="mb-8">
          <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-pill bg-surface-1 text-caption text-ink-muted">
            <span className="w-1.5 h-1.5 rounded-full bg-success-green" />
            Now in public beta
          </span>
        </div>

        {/* Headline */}
        <h1 className="text-display-xl text-ink max-w-[800px] mb-8">
          Ask for any web data.
          <br />
          Get it structured.
        </h1>

        {/* Subhead */}
        <p className="text-body-lg text-ink-muted max-w-[520px] mb-10">
          The only web scraping API with native Cloudflare bypass, structured JSON output,
          and Natural Language extraction — in one simple request.
        </p>

        {/* CTAs */}
        <div className="flex items-center gap-3 flex-wrap">
          <Link href="/register">
            <Button variant="primary" size="lg">Get started free →</Button>
          </Link>
          <Link href="/docs">
            <Button variant="secondary" size="lg">Read the docs</Button>
          </Link>
        </div>

        {/* Social proof */}
        <p className="text-caption text-ink-muted mt-8">
          500 req/month free · No credit card · Bypass Cloudflare Turnstile
        </p>
      </div>
    </section>
  );
}
