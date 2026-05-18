"use client";

import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { useSessionKey } from "@/hooks/useSessionKey";
import { useTopDomains } from "@/hooks/useUsageHistory";

export function RecentRequestsTable() {
  const { data: sk } = useSessionKey();
  const { data, isLoading } = useTopDomains(sk?.session_key ?? null);

  const domains = data?.domains ?? [];

  return (
    <Card>
      <p className="text-body-sm text-ink mb-2">Top domains this month</p>
      <p className="text-micro text-ink-muted mb-6">By request count</p>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </div>
      ) : domains.length === 0 ? (
        <div className="py-8 text-center text-caption text-ink-muted">
          No requests yet — make your first API call to see data here.
        </div>
      ) : (
        <div className="overflow-x-auto -mx-1">
          <table className="w-full text-caption">
            <thead>
              <tr className="text-ink-muted border-b border-border">
                <th className="text-left pb-3 pr-4 font-medium">Domain</th>
                <th className="text-right pb-3 font-medium">Requests</th>
              </tr>
            </thead>
            <tbody>
              {domains.map((row, i) => {
                const maxCount = domains[0]?.count ?? 1;
                const pct = Math.round((row.count / maxCount) * 100);
                return (
                  <tr key={row.domain} className="border-b border-border last:border-0">
                    <td className="py-2.5 pr-4">
                      <div className="flex items-center gap-3">
                        <span className="text-ink-muted w-4 text-right shrink-0">{i + 1}</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-ink font-mono truncate">{row.domain}</p>
                          <div className="mt-1 h-1 bg-surface-2 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full bg-[#0099FF]"
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="py-2.5 text-right text-ink tabular-nums">
                      {row.count.toLocaleString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
