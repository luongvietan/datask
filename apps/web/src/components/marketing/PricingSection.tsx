import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { Tick01Icon, ArrowRight01Icon } from "@hugeicons/core-free-icons";

interface PricingTier {
  name: string;
  price: string;
  unit: string;
  description: string;
  features: string[];
  cta: string;
  ctaHref: string;
  featured?: boolean;
}

const TIERS: PricingTier[] = [
  {
    name: "Free",
    price: "$0",
    unit: "500 req/month",
    description: "For prototyping and personal projects.",
    features: [
      "500 requests/month",
      "Layer 1 — Fetch",
      "Layer 2 — Schema extraction",
      "2 concurrent requests",
      "Community support",
    ],
    cta: "Get started",
    ctaHref: "/register",
  },
  {
    name: "Pay-as-you-go",
    price: "$0.005",
    unit: "per request",
    description: "For production agents. Pay only for what you use.",
    features: [
      "Unlimited requests",
      "Layer 1 + Layer 2",
      "10 concurrent requests",
      "60 req/min burst",
      "Email support",
      "Usage dashboard",
    ],
    cta: "Start free, upgrade anytime",
    ctaHref: "/register",
    featured: true,
  },
  {
    name: "Commit 10K",
    price: "$0.003",
    unit: "per request",
    description: "For teams with predictable volume. 40% cheaper.",
    features: [
      "10,000 req/month committed",
      "Layer 1 + Layer 2 + Layer 3",
      "20 concurrent requests",
      "120 req/min burst",
      "Priority support",
      "Webhook delivery",
    ],
    cta: "Contact us",
    ctaHref: "mailto:hi@datask.run",
  },
];

export function PricingSection({ showFullPage = false }: { showFullPage?: boolean }) {
  return (
    <section className="bg-canvas py-24 border-t border-hairline-soft">
      <div className="container-app">
        <p className="text-caption text-ink-muted uppercase tracking-widest mb-4">Pricing</p>
        <h2 className="text-display-lg text-ink mb-4">
          Simple, usage-based.
        </h2>
        <p className="text-body-lg text-ink-muted mb-12 max-w-[480px]">
          Free to start. Pay per successful request — not per attempt.
          Cheaper per successful scrape than every competitor.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {TIERS.map((tier) => (
            <Card key={tier.name} variant={tier.featured ? "featured" : "default"} className="flex flex-col gap-5">
              <div className="flex items-center justify-between">
                <span className="text-headline text-ink">{tier.name}</span>
                {tier.featured && <Badge variant="info">Most popular</Badge>}
              </div>

              <div>
                <span className="text-display-md text-ink">{tier.price}</span>
                <span className="text-caption text-ink-muted ml-2">{tier.unit}</span>
              </div>

              <p className="text-body text-ink-muted">{tier.description}</p>

              <ul className="space-y-2 flex-1">
                {tier.features.map((f) => (
                  <li key={f} className="text-caption text-ink-muted flex items-start gap-2">
                    <Icon icon={Tick01Icon as IconProp} size={14} className="text-success-green mt-0.5 shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>

              <Link href={tier.ctaHref}>
                <Button
                  variant={tier.featured ? "primary" : "secondary"}
                  className="w-full justify-center"
                >
                  {tier.cta}
                </Button>
              </Link>
            </Card>
          ))}
        </div>

        {!showFullPage && (
          <p className="text-caption text-ink-muted mt-8 text-center flex items-center justify-center gap-1 flex-wrap">
            <span>Need 100K+ req/month?</span>
            <a href="mailto:hi@datask.run" className="text-accent-blue hover:underline inline-flex items-center gap-1">
              Contact us for commit pricing
              <Icon icon={ArrowRight01Icon as IconProp} size={12} />
            </a>
          </p>
        )}
      </div>
    </section>
  );
}
