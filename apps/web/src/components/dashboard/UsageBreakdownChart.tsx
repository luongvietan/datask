import { Card } from "@/components/ui/Card";
export function UsageBreakdownChart() {
  return (
    <Card>
      <p className="text-body-sm text-ink mb-1">Daily requests</p>
      <div className="h-48 flex items-center justify-center border border-dashed border-hairline rounded-lg mt-4">
        <p className="text-caption text-ink-muted">recharts BarChart — Phase 2</p>
      </div>
    </Card>
  );
}
