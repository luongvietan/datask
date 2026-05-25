"use client";

import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { useSessionKey } from "@/hooks/useSessionKey";
import { useTopDomains } from "@/hooks/useUsageHistory";

export function DomainBreakdownTable() {
  const { data: sk } = useSessionKey();
  const { data, isLoading } = useTopDomains(sk?.session_key ?? null);

  const domains = data?.domains ?? [];

  return (
    <Card>
      <p className="text-body-sm text-ink mb-2">Top domains</p>
      <p className="text-micro text-ink-muted mb-6">Request counts by domain</p>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </div>
      ) : domains.length === 0 ? (
        <div className="py-8 text-center text-caption text-ink-muted">
          No requests yet — make your first API call to see domain data here.
        </div>
      ) : (
        <table className="w-full text-caption">
          <thead>
            <tr className="text-ink-muted border-b border-hairline-soft">
              <th className="text-left pb-3 font-medium">Domain</th>
              <th className="text-right pb-3 font-medium">Requests</th>
              <th className="text-right pb-3 font-medium">Share</th>
            </tr>
          </thead>
          <tbody>
            {domains.map((row) => {
              const totalCount = domains.reduce((sum, d) => sum + d.count, 0);
              const sharePct = totalCount > 0 ? Math.round((row.count / totalCount) * 100) : 0;
              return (
                <tr key={row.domain} className="border-b border-hairline-soft last:border-0">
                  <td className="py-3 text-ink font-mono">{row.domain}</td>
                  <td className="py-3 text-right text-ink tabular-nums">{row.count.toLocaleString()}</td>
                  <td className="py-3 text-right text-ink-muted tabular-nums">
                    {sharePct}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </Card>
  );
}
