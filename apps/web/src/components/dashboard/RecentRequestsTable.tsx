"use client";

import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { Badge } from "@/components/ui/Badge";
import { useSessionKey } from "@/hooks/useSessionKey";
import { useRequests } from "@/hooks/useRequests";
import { RequestDetailDrawer } from "@/components/dashboard/RequestDetailDrawer";
import type { RequestLogItem } from "@/types";

export function RecentRequestsTable() {
  const { data: sk } = useSessionKey();
  const [selectedRequest, setSelectedRequest] = useState<RequestLogItem | null>(null);
  const { data, isLoading, isError } = useRequests({
    apiKey: sk?.session_key ?? null,
    limit: 50,
  });

  const requests = data?.requests ?? [];

  const formatTime = (iso: string | null) => {
    if (!iso) return "—";
    return new Date(iso).toLocaleTimeString();
  };

  const formatLatency = (ms: number | null) => {
    if (ms == null) return "—";
    return `${ms}ms`;
  };

  return (
    <>
      <Card>
        <p className="text-body-sm text-ink mb-2">Recent requests</p>
        <p className="text-micro text-ink-muted mb-6">Last 50 API calls</p>

        {isLoading ? (
          <div className="space-y-3">
            {[...Array(10)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : isError ? (
          <div className="py-8 text-center text-caption text-ink-muted">
            Could not load requests. Please try again later.
          </div>
        ) : requests.length === 0 ? (
          <div className="py-8 text-center text-caption text-ink-muted">
            No requests yet — make your first API call to see data here.
          </div>
        ) : (
          <div className="overflow-x-auto -mx-1">
            <table className="w-full text-caption">
              <thead>
                <tr className="text-ink-muted border-b border-border">
                  <th className="text-left pb-3 pr-4 font-medium">Time</th>
                  <th className="text-left pb-3 pr-4 font-medium">URL</th>
                  <th className="text-center pb-3 pr-4 font-medium">Layer</th>
                  <th className="text-center pb-3 pr-4 font-medium">Status</th>
                  <th className="text-right pb-3 pr-4 font-medium">Credits</th>
                  <th className="text-right pb-3 font-medium">Latency</th>
                </tr>
              </thead>
              <tbody>
                {requests.map((req) => (
                  <tr
                    key={req.request_id ?? req.url + req.created_at}
                    className="border-b border-border last:border-0 cursor-pointer hover:bg-surface-2 transition-colors"
                    onClick={() => setSelectedRequest(req)}
                  >
                    <td className="py-3 pr-4 text-ink-muted whitespace-nowrap">
                      {formatTime(req.created_at)}
                    </td>
                    <td className="py-3 pr-4">
                      <p className="text-ink font-mono truncate max-w-[300px]" title={req.url}>
                        {req.url}
                      </p>
                    </td>
                    <td className="py-3 pr-4 text-center">
                      <Badge variant="info">L{req.layer}</Badge>
                    </td>
                    <td className="py-3 pr-4 text-center">
                      <Badge variant={req.success ? "success" : "error"}>
                        {req.success ? "✓" : "✗"}
                      </Badge>
                    </td>
                    <td className="py-3 pr-4 text-right text-ink tabular-nums">
                      {req.credits_used}
                    </td>
                    <td className="py-3 text-right text-ink-muted tabular-nums">
                      {formatLatency(req.response_time_ms)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <RequestDetailDrawer
        request={selectedRequest}
        onClose={() => setSelectedRequest(null)}
      />
    </>
  );
}
