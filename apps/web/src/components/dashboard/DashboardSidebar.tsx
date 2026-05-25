"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import { Icon, type IconProp } from "@/components/ui/Icon";
import {
  LayoutGridIcon,
  TerminalIcon,
  AnalyticsUpIcon,
  ApiIcon,
  CreditCardIcon,
  HelpCircleIcon,
  Cancel01Icon,
} from "@hugeicons/core-free-icons";

const NAV_ITEMS: { href: string; label: string; icon: IconProp }[] = [
  { href: "/dashboard", label: "Overview", icon: LayoutGridIcon as IconProp },
  { href: "/playground", label: "Playground", icon: TerminalIcon as IconProp },
  { href: "/usage", label: "Usage", icon: AnalyticsUpIcon as IconProp },
  { href: "/keys", label: "API Keys", icon: ApiIcon as IconProp },
  { href: "/billing", label: "Billing", icon: CreditCardIcon as IconProp },
];

interface DashboardSidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function DashboardSidebar({ isOpen = false, onClose }: DashboardSidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/60 lg:hidden backdrop-blur-sm animate-fade-in"
          onClick={onClose}
        />
      )}

      <aside
        className={clsx(
          "flex flex-col fixed left-0 top-0 bottom-0 w-[240px] bg-canvas border-r border-hairline-soft z-40 py-5 transition-transform duration-300 ease-in-out",
          "lg:translate-x-0 lg:flex",
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        <div className="px-5 mb-8 flex items-center justify-between">
          <Link href="/" className="text-[20px] font-medium tracking-[-0.8px] text-ink">
            Datask
          </Link>
          <button
            onClick={onClose}
            className="lg:hidden p-1 text-ink-muted hover:text-ink transition-colors focus:outline-none"
            aria-label="Close sidebar"
          >
            <Icon icon={Cancel01Icon as IconProp} size={18} />
          </button>
        </div>

        <nav className="flex-1 px-3 space-y-0.5">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={clsx(
                  "flex items-center gap-3 px-3 py-2.5 rounded-md",
                  "text-body-sm transition-colors",
                  isActive
                    ? "bg-surface-1 text-ink font-medium"
                    : "text-ink-muted hover:bg-surface-1 hover:text-ink"
                )}
              >
                <Icon
                  icon={item.icon}
                  size={16}
                  className={clsx(
                    "shrink-0 transition-colors",
                    isActive ? "text-ink" : "text-ink-muted"
                  )}
                />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="px-3 pt-4 border-t border-hairline-soft space-y-1">
          <Link
            href="/docs"
            onClick={onClose}
            className="flex items-center gap-3 px-3 py-2.5 rounded-md text-body-sm text-ink-muted hover:bg-surface-1 hover:text-ink transition-colors"
          >
            <Icon icon={HelpCircleIcon as IconProp} size={16} className="shrink-0" />
            Docs
          </Link>
        </div>
      </aside>
    </>
  );
}
