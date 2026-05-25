"use client";

import { useUsage } from "@/hooks/useUsage";
import { useSessionKey } from "@/hooks/useSessionKey";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { Alert01Icon, StopCircleIcon } from "@hugeicons/core-free-icons";

export function BudgetProgressBar() {
  const { data: sk } = useSessionKey();
  const { data: usage } = useUsage(sk?.session_key ?? null);

  if (!usage || usage.budget === null || usage.budget === undefined) return null;

  const budget = usage.budget;
  const used = usage.used ?? usage.credits_used;
  const remaining = usage.remaining ?? Math.max(0, budget - used);
  const pct = budget > 0 ? Math.round((used / budget) * 100) : 0;
  const isExceeded = used >= budget;
  const isWarning = pct >= (usage.alert_threshold ?? 80);

  const barColor = isExceeded
    ? "linear-gradient(90deg, #EF4444, #F87171)"
    : isWarning
      ? "linear-gradient(90deg, #CA8A04, #FACC15)"
      : "linear-gradient(90deg, #0099FF, #60C0FF)";

  return (
    <div className="bg-surface-1 rounded-xl px-5 py-4">
      <div className="flex items-center justify-between mb-2">
        <span className={`text-caption flex items-center gap-1.5 ${
          isExceeded ? "text-[#EF4444]" : isWarning ? "text-[#FACC15]" : "text-ink-muted"
        }`}>
          <Icon
            icon={(isExceeded ? StopCircleIcon : isWarning ? Alert01Icon : Alert01Icon) as IconProp}
            size={14}
            className="shrink-0"
          />
          {isExceeded ? "Budget exceeded" : isWarning ? "Approaching budget limit" : "Monthly credit usage"}
        </span>
        <span className="text-caption text-ink-muted">
          {used.toLocaleString()} / {budget.toLocaleString()} credits
        </span>
      </div>

      <div className="h-2 bg-surface-2 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${Math.min(pct, 100)}%`,
            background: barColor,
          }}
        />
      </div>

      <div className="flex justify-between mt-1.5">
        <span className="text-caption text-ink-muted">
          {remaining.toLocaleString()} remaining
        </span>
        {usage.resets_at && (
          <span className="text-caption text-ink-muted">
            Resets {new Date(usage.resets_at).toLocaleDateString()}
          </span>
        )}
      </div>
    </div>
  );
}
