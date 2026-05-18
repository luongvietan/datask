"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: "▦" },
  { href: "/usage", label: "Usage", icon: "↗" },
  { href: "/keys", label: "API Keys", icon: "⌘" },
  { href: "/billing", label: "Billing", icon: "◈" },
];

export function DashboardSidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex flex-col fixed left-0 top-0 bottom-0 w-[240px] bg-canvas border-r border-hairline-soft z-40 py-5">
      {/* Wordmark */}
      <div className="px-5 mb-8">
        <Link href="/" className="text-[20px] font-medium tracking-[-0.8px] text-ink">
          Datask
        </Link>
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-3 space-y-0.5">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-md",
                "text-body-sm transition-colors",
                isActive
                  ? "bg-surface-1 text-ink"
                  : "text-ink-muted hover:bg-surface-1 hover:text-ink"
              )}
            >
              <span className="text-[15px] opacity-70">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Bottom: account + docs link */}
      <div className="px-3 pt-4 border-t border-hairline-soft space-y-1">
        <Link
          href="/docs"
          className="flex items-center gap-3 px-3 py-2.5 rounded-md text-body-sm text-ink-muted hover:bg-surface-1 hover:text-ink transition-colors"
        >
          <span className="text-[15px] opacity-70">?</span>
          Docs
        </Link>
      </div>
    </aside>
  );
}
