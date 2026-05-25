"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { Card } from "@/components/ui/Card";
import { useSessionKey } from "@/hooks/useSessionKey";
import { useRequests } from "@/hooks/useRequests";
import { Skeleton } from "@/components/ui/Skeleton";

const COLORS = ["#0099FF", "#A855F7", "#F59E0B"];

export function LayerBreakdownChart() {
  const { data: sk } = useSessionKey();
  const { data, isLoading, isError } = useRequests({
    apiKey: sk?.session_key ?? null,
    limit: 200,
  });

  const requests = data?.requests ?? [];

  // Aggregate by layer
  const layerCounts = requests.reduce(
    (acc, req) => {
      acc[`L${req.layer}`] = (acc[`L${req.layer}`] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  const chartData = Object.entries(layerCounts)
    .map(([name, value]) => ({ name, value }))
    .filter((d) => d.value > 0)
    .sort((a, b) => a.name.localeCompare(b.name));

  const total = requests.length;

  return (
    <Card>
      <p className="text-body-sm text-ink mb-1">Layer breakdown</p>
      <p className="text-caption text-ink-muted mb-4">Distribution by extraction layer</p>

      {isLoading && <Skeleton className="h-48 w-full rounded-lg" />}

      {isError && (
        <div className="h-48 flex items-center justify-center">
          <p className="text-caption text-ink-muted">Could not load data.</p>
        </div>
      )}

      {data && total === 0 && (
        <div className="h-48 flex items-center justify-center border border-dashed border-hairline rounded-lg">
          <p className="text-caption text-ink-muted">No requests yet.</p>
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
            <div>
              <p className="text-display-md text-ink leading-none">{total}</p>
              <p className="text-caption text-ink-muted mt-1">total requests</p>
            </div>
            <div className="space-y-1.5">
              {chartData.map((item, i) => {
                const pct = Math.round((item.value / total) * 100);
                return (
                  <div key={item.name} className="flex items-center gap-2">
                    <span
                      className="w-2 h-2 rounded-full shrink-0"
                      style={{ background: COLORS[i % COLORS.length] }}
                    />
                    <span className="text-caption text-ink-muted">
                      {item.name}
                    </span>
                    <span className="text-caption text-ink ml-auto tabular-nums">
                      {item.value} ({pct}%)
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
