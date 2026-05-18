import Link from "next/link";
import { Button } from "@/components/ui/Button";

const NAV_LINKS = [
  { href: "/pricing", label: "Pricing" },
  { href: "/docs", label: "Docs" },
];

export function TopNav() {
  return (
    <header className="sticky top-0 z-50 bg-canvas border-b border-hairline-soft">
      <div className="container-app h-14 flex items-center justify-between gap-6">
        {/* Wordmark */}
        <Link href="/" className="text-[22px] font-medium tracking-[-0.8px] text-ink shrink-0">
          Datask
        </Link>

        {/* Center nav links — hidden on mobile */}
        <nav className="hidden md:flex items-center gap-6">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-caption text-ink-muted hover:text-ink transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Right CTAs */}
        <div className="flex items-center gap-2">
          <Link href="/login">
            <Button variant="secondary" size="sm">Sign in</Button>
          </Link>
          <Link href="/register">
            <Button variant="primary" size="sm">Get started</Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
