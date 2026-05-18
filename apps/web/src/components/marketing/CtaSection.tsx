import Link from "next/link";
import { Button } from "@/components/ui/Button";

export function CtaSection() {
  return (
    <section className="bg-canvas py-24 border-t border-hairline-soft">
      <div className="container-app text-center">
        <h2 className="text-display-xl text-ink mb-6">
          Try the URL that<br />Firecrawl couldn&apos;t scrape.
        </h2>
        <p className="text-body-lg text-ink-muted mb-10 max-w-[400px] mx-auto">
          No signup. Just paste a Cloudflare-protected URL.
        </p>
        <Link href="/register">
          <Button variant="primary" size="lg">Get 500 free requests →</Button>
        </Link>
      </div>
    </section>
  );
}
