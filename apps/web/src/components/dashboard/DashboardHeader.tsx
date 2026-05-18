"use client";

import { Button } from "@/components/ui/Button";

export function DashboardHeader() {
  return (
    <header className="h-14 border-b border-hairline-soft flex items-center justify-between px-6 lg:px-8 shrink-0">
      <div />
      <div className="flex items-center gap-3">
        <span className="text-caption text-ink-muted hidden sm:block">
          Free tier · 342 / 500 req
        </span>
        <Button variant="primary" size="sm">Upgrade</Button>
      </div>
    </header>
  );
}
