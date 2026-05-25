import type { Metadata } from "next";
import { BudgetAlertBanner } from "@/components/dashboard/BudgetAlertBanner";
import { BudgetProgressBar } from "@/components/dashboard/BudgetProgressBar";
import { UsageBreakdownChart } from "@/components/dashboard/UsageBreakdownChart";
import { DomainBreakdownTable } from "@/components/dashboard/DomainBreakdownTable";
import { LayerBreakdownChart } from "@/components/dashboard/LayerBreakdownChart";
import { RecentRequestsTable } from "@/components/dashboard/RecentRequestsTable";

export const metadata: Metadata = { title: "Usage" };

export default function UsagePage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-display-md text-ink">Usage</h1>
        <p className="text-body text-ink-muted mt-1">
          Requests, success rates, and domain breakdown
        </p>
      </div>
      <BudgetAlertBanner />
      <BudgetProgressBar />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <UsageBreakdownChart />
        <LayerBreakdownChart />
      </div>
      <RecentRequestsTable />
      <DomainBreakdownTable />
    </div>
  );
}
