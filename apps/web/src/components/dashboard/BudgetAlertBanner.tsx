"use client";

import { useState } from "react";
import { useSessionKey } from "@/hooks/useSessionKey";
import { useUsage } from "@/hooks/useUsage";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { Badge } from "@/components/ui/Badge";
import { Alert01Icon, Cancel01Icon } from "@hugeicons/core-free-icons";
import Link from "next/link";

export function BudgetAlertBanner() {
  const { data: sk } = useSessionKey();
  const { data: usage } = useUsage(sk?.session_key ?? null);
  const [dismissed, setDismissed] = useState(false);

  if (dismissed || !usage || !usage.alert_level || usage.alert_level === "none") {
    return null;
  }

  const isExceeded = usage.alert_level === "exceeded";
  const isWarning = usage.alert_level === "warning";

  const bgClass = isExceeded
    ? "bg-[rgba(239,68,68,0.08)] border-[#EF4444]"
    : isWarning
      ? "bg-[rgba(234,179,8,0.08)] border-[#FACC15]"
      : "";

  const textClass = isExceeded
    ? "text-[#F87171]"
    : isWarning
      ? "text-[#FACC15]"
      : "";

  const badgeVariant = isExceeded ? "error" : isWarning ? "warning" : "default";

  const pct = usage.budget && usage.budget > 0
    ? Math.round((usage.used / usage.budget) * 100)
    : 0;

  const message = isExceeded
    ? `Budget exceeded — ${usage.used.toLocaleString()}/${usage.budget?.toLocaleString()} credits used (${pct}%)`
    : `You've used ${pct}% of your monthly budget (${usage.used.toLocaleString()}/${usage.budget?.toLocaleString()} credits)`;

  const ctaText = isExceeded ? "Increase budget" : "Manage budget";

  return (
    <div
      className={`rounded-xl border px-5 py-4 flex items-start gap-3 ${bgClass}`}
      role="alert"
    >
      <div className={`mt-0.5 ${textClass}`}>
        <Icon
          icon={(isExceeded ? Cancel01Icon : Alert01Icon) as IconProp}
          size={20}
          className="shrink-0"
        />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-start gap-2 mb-1">
          <Badge variant={badgeVariant}>{isExceeded ? "Exceeded" : "Warning"}</Badge>
          <p className={`text-body font-medium ${textClass}`}>{message}</p>
        </div>

        <p className="text-caption text-ink-muted">
          {isExceeded
            ? "New requests will be blocked until you increase your budget or it resets next month."
            : "Consider increasing your budget to avoid interruptions."}
        </p>

        <div className="mt-3 flex items-center gap-3">
          <Link
            href="/billing"
            className={`text-caption font-medium underline ${textClass}`}
          >
            {ctaText}
          </Link>

          <button
            onClick={() => setDismissed(true)}
            className="text-caption text-ink-muted hover:text-ink transition-colors"
            aria-label="Dismiss alert"
          >
            Dismiss
          </button>
        </div>
      </div>

      <button
        onClick={() => setDismissed(true)}
        className={`shrink-0 ${textClass} hover:opacity-70 transition-opacity`}
        aria-label="Close alert"
      >
        <Icon icon={Cancel01Icon as IconProp} size={18} />
      </button>
    </div>
  );
}
