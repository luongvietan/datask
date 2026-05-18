"use client";

import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { useSessionKey } from "@/hooks/useSessionKey";
import { useUsageHistory } from "@/hooks/useUsageHistory";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function RequestsChart() {
  const { data: sk } = useSessionKey();
  const { data, isLoading } = useUsageHistory(sk?.session_key ?? null);

  const history = data?.history ?? [];

  return (
    <Card>
      <p className="text-body-sm text-ink mb-1">Requests over time</p>
      <p className="text-micro text-ink-muted mb-6">Last 30 days</p>

      {isLoading ? (
        <Skeleton className="h-48 w-full" />
      ) : history.length === 0 ? (
        <div className="h-48 flex items-center justify-center border border-dashed border-border rounded-lg">
          <p className="text-caption text-ink-muted">No data yet — make your first API request.</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={192}>
          <LineChart data={history} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: "rgba(255,255,255,0.4)" }}
              tickFormatter={(val: string) => val.slice(5)}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "rgba(255,255,255,0.4)" }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                background: "#1A1A1A",
                border: "1px solid rgba(255,255,255,0.12)",
                borderRadius: 8,
                fontSize: 12,
              }}
              labelStyle={{ color: "rgba(255,255,255,0.6)" }}
            />
            <Line
              type="monotone"
              dataKey="requests"
              stroke="#0099FF"
              strokeWidth={2}
              dot={false}
              name="Total"
            />
            <Line
              type="monotone"
              dataKey="successful"
              stroke="#22C55E"
              strokeWidth={2}
              dot={false}
              name="Successful"
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
}
