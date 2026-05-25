"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { Card } from "@/components/ui/Card";
import { useUsage } from "@/hooks/useUsage";
import { useSessionKey } from "@/hooks/useSessionKey";
import { Skeleton } from "@/components/ui/Skeleton";

const COLORS = ["#22C55E", "#EF4444", "#0099FF"];

export function LayerBreakdownChart() {
  const { data: sk } = useSessionKey();
  const { data, isLoading, isError } = useUsage(sk?.session_key ?? null);

  const chartData =
    data
      ? [
          { name: "Successful", value: data.successful_requests },
          { name: "Failed", value: data.failed_requests },
        ].filter((d) => d.value > 0)
      : [];

  const total = data?.current_month_requests ?? 0;
  const rate =
    total > 0 ? Math.round((data!.successful_requests / total) * 100) : null;

  return (
    <Card>
      <p className="text-body-sm text-ink mb-1">Success rate</p>
      <p className="text-caption text-ink-muted mb-4">This billing period</p>

      {isLoading && <Skeleton className="h-48 w-full rounded-lg" />}

      {isError && (
        <div className="h-48 flex items-center justify-center">
          <p className="text-caption text-ink-muted">Could not load data.</p>
        </div>
      )}

      {data && total === 0 && (
        <div className="h-48 flex items-center justify-center border border-dashed border-hairline rounded-lg">
          <p className="text-caption text-ink-muted">No requests yet this period.</p>
        </div>
      )}

      {data && total > 0 && (
        <div className="flex items-center gap-6">
          <ResponsiveContainer width={160} height={160}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={46}
                outerRadius={72}
                paddingAngle={2}
                dataKey="value"
                strokeWidth={0}
              >
                {chartData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "#1A1A1A",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 8,
                  fontSize: 12,
                  color: "#fff",
                }}
              />
            </PieChart>
          </ResponsiveContainer>

          <div className="space-y-3 flex-1">
            {rate !== null && (
              <div>
                <p className="text-display-md text-ink leading-none">{rate}%</p>
                <p className="text-caption text-ink-muted mt-1">success rate</p>
              </div>
            )}
            <div className="space-y-1.5">
              {chartData.map((item, i) => (
                <div key={item.name} className="flex items-center gap-2">
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ background: COLORS[i % COLORS.length] }}
                  />
                  <span className="text-caption text-ink-muted">
                    {item.name}
                  </span>
                  <span className="text-caption text-ink ml-auto">
                    {item.value.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
