import Link from "next/link";

const FOOTER_COLUMNS = [
  {
    title: "Product",
    links: [
      { href: "/", label: "Home" },
      { href: "/pricing", label: "Pricing" },
      { href: "/docs", label: "Docs" },
      { href: "/blog/turnstile-benchmark-2026", label: "Benchmark" },
    ],
  },
  {
    title: "API",
    links: [
      { href: "/docs#layer1", label: "Layer 1 — Fetch" },
      { href: "/docs#layer2", label: "Layer 2 — Extract" },
      { href: "/docs#layer3", label: "Layer 3 — NL Prompt" },
    ],
  },
  {
    title: "Legal",
    links: [
      { href: "/terms", label: "Terms" },
      { href: "/privacy", label: "Privacy" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="bg-canvas border-t border-hairline-soft">
      <div className="container-app py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
          {/* Brand column */}
          <div className="col-span-2 md:col-span-1">
            <span className="text-[22px] font-medium tracking-[-0.8px] text-ink">Datask</span>
            <p className="text-caption text-ink-muted mt-3 leading-relaxed">
              Web Data API for AI Agents.
              <br />
              Ask for any web data. Get it structured.
            </p>
          </div>

          {/* Link columns */}
          {FOOTER_COLUMNS.map((col) => (
            <div key={col.title}>
              <p className="text-caption font-medium text-ink mb-4">{col.title}</p>
              <ul className="space-y-3">
                {col.links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-caption text-ink-muted hover:text-ink transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="divider-soft pt-8">
          <p className="text-micro text-ink-muted">
            © {new Date().getFullYear()} Datask. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
