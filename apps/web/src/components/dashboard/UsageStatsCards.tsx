"use client";

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { useUsage } from "@/hooks/useUsage";
import { useSessionKey } from "@/hooks/useSessionKey";

export function UsageStatsCards() {
  const { data: sk } = useSessionKey();
  const { data: usage, isLoading, error } = useUsage(sk?.session_key ?? null);

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="flex flex-col gap-3">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-3 w-40" />
          </Card>
        ))}
      </div>
    );
  }

  if (error || !usage) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <Card className="col-span-full text-center text-ink-muted text-body-sm py-8">
          Failed to load usage data.
        </Card>
      </div>
    );
  }

  const successRate =
    usage.current_month_requests > 0
      ? ((usage.successful_requests / usage.current_month_requests) * 100).toFixed(1)
      : "100.0";

  const quotaLabel =
    usage.quota_remaining !== null
      ? `${usage.current_month_requests} of ${usage.current_month_requests + usage.quota_remaining} free`
      : `${usage.current_month_requests} (pay-as-you-go)`;

  const quotaPct =
    usage.quota_remaining !== null
      ? Math.round(
          (usage.current_month_requests /
            (usage.current_month_requests + usage.quota_remaining)) *
            100
        )
      : null;

  const stats = [
    {
      label: "Requests this month",
      value: usage.current_month_requests.toLocaleString(),
      sub: quotaLabel,
      badge:
        quotaPct !== null
          ? {
              label: `${quotaPct}% used`,
              variant: (quotaPct >= 100 ? "error" : quotaPct >= 80 ? "warning" : "success") as
                | "success"
                | "warning"
                | "error",
            }
          : undefined,
    },
    {
      label: "Success rate",
      value: `${successRate}%`,
      sub: `${usage.successful_requests} succeeded · ${usage.failed_requests} failed`,
      badge:
        parseFloat(successRate) >= 95
          ? { label: "Healthy", variant: "success" as const }
          : { label: "Degraded", variant: "warning" as const },
    },
    {
      label: "Credits used",
      value: usage.credits_used.toLocaleString(),
      sub: `Tier: ${usage.tier}`,
    },
    {
      label: "Current tier",
      value: usage.tier === "free" ? "Free" : "PAYG",
      sub: usage.billing_period_end ? `Billing ends ${usage.billing_period_end.slice(0, 10)}` : "No billing cycle",
      badge:
        usage.tier === "free"
          ? { label: "Free", variant: "info" as const }
          : { label: "Active", variant: "success" as const },
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <Card key={stat.label} className="flex flex-col gap-3">
          <p className="text-caption text-ink-muted">{stat.label}</p>
          <div className="flex items-end gap-2">
            <span className="text-display-md text-ink">{stat.value}</span>
            {stat.badge && (
              <Badge variant={stat.badge.variant} className="mb-1">
                {stat.badge.label}
              </Badge>
            )}
          </div>
          <p className="text-micro text-ink-muted">{stat.sub}</p>
        </Card>
      ))}
    </div>
  );
}
