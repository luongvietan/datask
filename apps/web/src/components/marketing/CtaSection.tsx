import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { ArrowRight01Icon } from "@hugeicons/core-free-icons";

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
          <Button variant="primary" size="lg">
            <span className="inline-flex items-center gap-2">
              Get 500 free requests
              <Icon icon={ArrowRight01Icon as IconProp} size={16} />
            </span>
          </Button>
        </Link>
      </div>
    </section>
  );
}
