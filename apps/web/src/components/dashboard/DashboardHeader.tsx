"use client";

import { Button } from "@/components/ui/Button";
import { HugeiconsIcon, type HugeiconsIconProps } from "@hugeicons/react";
import { Menu01Icon } from "@hugeicons/core-free-icons";

type IconProp = HugeiconsIconProps["icon"];

interface DashboardHeaderProps {
  onMenuClick?: () => void;
}

export function DashboardHeader({ onMenuClick }: DashboardHeaderProps) {
  return (
    <header className="h-14 border-b border-hairline-soft flex items-center justify-between px-6 lg:px-8 shrink-0">
      <button
        onClick={onMenuClick}
        className="lg:hidden p-1.5 rounded-lg text-ink-muted hover:text-ink bg-surface-1 border border-hairline-soft transition-colors focus:outline-none"
        aria-label="Open sidebar"
      >
        <HugeiconsIcon icon={Menu01Icon as IconProp} size={18} strokeWidth={1.5} />
      </button>
      <div className="hidden lg:block" />

      <div className="flex items-center gap-3">
        <span className="text-caption text-ink-muted hidden sm:block">
          Free tier · 342 / 500 req
        </span>
        <Button variant="primary" size="sm">Upgrade</Button>
      </div>
    </header>
  );
}
