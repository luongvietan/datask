"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card } from "@/components/ui/Card";
import { useUsageHistory } from "@/hooks/useUsageHistory";
import { useSessionKey } from "@/hooks/useSessionKey";
import { Skeleton } from "@/components/ui/Skeleton";

function formatDate(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function UsageBreakdownChart() {
  const { data: sk } = useSessionKey();
  const { data, isLoading, isError } = useUsageHistory(sk?.session_key ?? null);

  return (
    <Card>
      <p className="text-body-sm text-ink mb-1">Daily requests</p>
      <p className="text-caption text-ink-muted mb-4">Last 30 days</p>

      {isLoading && <Skeleton className="h-48 w-full rounded-lg" />}

      {isError && (
        <div className="h-48 flex items-center justify-center">
          <p className="text-caption text-ink-muted">Could not load usage data.</p>
        </div>
      )}

      {data && data.history.length === 0 && (
        <div className="h-48 flex items-center justify-center border border-dashed border-hairline rounded-lg">
          <p className="text-caption text-ink-muted">No requests yet this month.</p>
        </div>
      )}

      {data && data.history.length > 0 && (
        <ResponsiveContainer width="100%" height={192}>
          <BarChart data={data.history} margin={{ top: 4, right: 0, left: -20, bottom: 0 }}>
            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              tick={{ fontSize: 11, fill: "#999" }}
              axisLine={false}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 11, fill: "#999" }}
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip
              contentStyle={{
                background: "#1A1A1A",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 8,
                fontSize: 12,
                color: "#fff",
              }}
              labelFormatter={(v) => formatDate(v as string)}
              formatter={(value: number, name: string) => [
                value,
                name === "successful" ? "Successful" : "Total",
              ]}
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
            />
            <Bar dataKey="requests" fill="rgba(0,153,255,0.25)" radius={[3, 3, 0, 0]} name="requests" />
            <Bar dataKey="successful" fill="#0099FF" radius={[3, 3, 0, 0]} name="successful" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
}
