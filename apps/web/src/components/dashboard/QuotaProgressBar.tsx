"use client";

import { useUsage } from "@/hooks/useUsage";
import { useSessionKey } from "@/hooks/useSessionKey";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { Alert01Icon } from "@hugeicons/core-free-icons";
import { UpgradeButton } from "./UpgradeButton";

export function QuotaProgressBar() {
  const { data: sk } = useSessionKey();
  const { data: usage } = useUsage(sk?.session_key ?? null);

  if (!usage || usage.quota_remaining === null) return null;

  const total = usage.current_month_requests + usage.quota_remaining;
  const used = usage.current_month_requests;
  const pct = total > 0 ? Math.round((used / total) * 100) : 0;
  const isWarning = pct >= 80;

  if (pct < 60) return null;

  return (
    <div className="bg-surface-1 rounded-xl px-5 py-4 flex items-center gap-4">
      <div className="flex-1 min-w-0">
        <div className="flex justify-between text-caption mb-2">
          <span className={isWarning ? "text-[#FACC15] flex items-center gap-1.5" : "text-ink-muted"}>
            {isWarning && <Icon icon={Alert01Icon as IconProp} size={14} className="shrink-0" />}
            {isWarning ? "Approaching free tier limit" : "Free tier usage"}
          </span>
          <span className="text-ink-muted">
            {used.toLocaleString()} / {total.toLocaleString()} requests
          </span>
        </div>
        <div className="h-1.5 bg-surface-2 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all"
            style={{
              width: `${Math.min(pct, 100)}%`,
              background: isWarning
                ? "linear-gradient(90deg, #CA8A04, #FACC15)"
                : "linear-gradient(90deg, #0099FF, #60C0FF)",
            }}
          />
        </div>
      </div>
      <div className="shrink-0">
        <UpgradeButton />
      </div>
    </div>
  );
}
