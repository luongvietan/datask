import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { HugeiconsIcon, type HugeiconsIconProps } from "@hugeicons/react";
import {
  AlertCircleIcon,
  CheckListIcon,
  SparklesIcon,
  ArrowUpRightStackIcon,
} from "@hugeicons/core-free-icons";

type IconProp = HugeiconsIconProps["icon"];

export function HeroSection() {
  return (
    <section className="bg-canvas pt-24 pb-20 lg:pt-32 lg:pb-28">
      <div className="container-app">
        {/* Eyebrow */}
        <div className="mb-8 flex flex-wrap items-center gap-3">
          <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-pill bg-surface-1 text-caption text-ink-muted">
            <span className="w-1.5 h-1.5 rounded-full bg-success-green animate-pulse" />
            Now in public beta
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-pill bg-surface-1 text-caption text-ink-muted border border-hairline">
            <HugeiconsIcon icon={AlertCircleIcon as IconProp} size={13} strokeWidth={1.5} className="text-[#F59E0B] shrink-0" />
            Firecrawl fails on Turnstile. We don&apos;t.
          </span>
        </div>

        {/* Headline */}
        <h1 className="text-display-xl text-ink max-w-[800px] mb-8">
          Ask for any web data.
          <br />
          <span className="text-accent-blue">Get it structured.</span>
        </h1>

        {/* Subhead */}
        <p className="text-body-lg text-ink-muted max-w-[520px] mb-10">
          The only web scraping API with native Cloudflare Turnstile bypass, structured JSON output,
          and Natural Language extraction — in one simple request.
        </p>

        {/* CTAs */}
        <div className="flex items-center gap-3 flex-wrap mb-10">
          <Link href="/register">
            <Button variant="primary" size="lg">Get started free →</Button>
          </Link>
          <Link href="/docs">
            <Button variant="secondary" size="lg">Read the docs</Button>
          </Link>
        </div>

        {/* Metrics row */}
        <div className="flex flex-wrap items-center gap-x-8 gap-y-4 border-t border-hairline-soft pt-8">
          {[
            { stat: ">95%", label: "success rate on Cloudflare-protected sites", icon: CheckListIcon as IconProp },
            { stat: "$0.005", label: "per request — no fixed monthly seat", icon: SparklesIcon as IconProp },
            { stat: "3 layers", label: "Fetch → Schema → Natural Language", icon: ArrowUpRightStackIcon as IconProp },
            { stat: "500 req", label: "free tier, no credit card", icon: CheckListIcon as IconProp },
          ].map(({ stat, label, icon }) => (
            <div key={stat} className="flex items-start gap-2.5">
              <HugeiconsIcon icon={icon} size={18} strokeWidth={1.5} className="text-accent-blue shrink-0 mt-0.5" />
              <div>
                <p className="text-display-md text-ink leading-none">{stat}</p>
                <p className="text-caption text-ink-muted mt-1 max-w-[140px] leading-snug">{label}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
