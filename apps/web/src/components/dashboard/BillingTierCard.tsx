import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

export function BillingTierCard() {
  return (
    <Card variant="featured" className="flex items-start justify-between gap-6">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-headline text-ink">Free tier</span>
          <Badge variant="info">Current plan</Badge>
        </div>
        <p className="text-body text-ink-muted">500 requests/month · No credit card required</p>
        <ul className="mt-4 space-y-1 text-caption text-ink-muted">
          <li>✓ Layer 1 — Fetch (Cloudflare bypass)</li>
          <li>✓ Layer 2 — Schema extraction</li>
          <li>✗ Layer 3 — Natural Language extraction</li>
          <li>✗ Webhooks</li>
        </ul>
      </div>
      <div className="text-right shrink-0">
        <span className="text-display-md text-ink">$0</span>
        <p className="text-caption text-ink-muted">/month</p>
      </div>
    </Card>
  );
}
