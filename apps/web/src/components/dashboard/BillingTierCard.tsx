import type { ReactNode } from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { Tick01Icon, CancelCircleIcon } from "@hugeicons/core-free-icons";

function FeatureItem({ included, children }: { included: boolean; children: ReactNode }) {
  return (
    <li className="flex items-start gap-2 text-caption text-ink-muted">
      <Icon
        icon={(included ? Tick01Icon : CancelCircleIcon) as IconProp}
        size={14}
        className={included ? "text-success-green mt-0.5 shrink-0" : "text-ink-muted opacity-50 mt-0.5 shrink-0"}
      />
      {children}
    </li>
  );
}

export function BillingTierCard() {
  return (
    <Card variant="featured" className="flex items-start justify-between gap-6">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-headline text-ink">Free tier</span>
          <Badge variant="info">Current plan</Badge>
        </div>
        <p className="text-body text-ink-muted">500 requests/month · No credit card required</p>
        <ul className="mt-4 space-y-1">
          <FeatureItem included>Layer 1 — Fetch (Cloudflare bypass)</FeatureItem>
          <FeatureItem included>Layer 2 — Schema extraction</FeatureItem>
          <FeatureItem included={false}>Layer 3 — Natural Language extraction</FeatureItem>
          <FeatureItem included={false}>Webhooks</FeatureItem>
        </ul>
      </div>
      <div className="text-right shrink-0">
        <span className="text-display-md text-ink">$0</span>
        <p className="text-caption text-ink-muted">/month</p>
      </div>
    </Card>
  );
}
