import type { Metadata } from "next";
import { UsageStatsCards } from "@/components/dashboard/UsageStatsCards";
import { RequestsChart } from "@/components/dashboard/RequestsChart";
import { RecentRequestsTable } from "@/components/dashboard/RecentRequestsTable";
import { QuotaProgressBar } from "@/components/dashboard/QuotaProgressBar";

export const metadata: Metadata = { title: "Dashboard" };

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Page title */}
      <div>
        <h1 className="text-display-md text-ink">Dashboard</h1>
        <p className="text-body text-ink-muted mt-1">Current billing period</p>
      </div>

      {/* Quota warning bar */}
      <QuotaProgressBar />

      {/* Stats overview */}
      <UsageStatsCards />

      {/* Requests over time chart */}
      <RequestsChart />

      {/* Recent requests */}
      <RecentRequestsTable />
    </div>
  );
}
