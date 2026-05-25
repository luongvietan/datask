import type { Metadata } from "next";
import { BillingTierCard } from "@/components/dashboard/BillingTierCard";
import { BudgetSettingsCard } from "@/components/dashboard/BudgetSettingsCard";
import { InvoicesList } from "@/components/dashboard/InvoicesList";
import { UpgradeButton } from "@/components/dashboard/UpgradeButton";

export const metadata: Metadata = { title: "Billing" };

export default function BillingPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-display-md text-ink">Billing</h1>
          <p className="text-body text-ink-muted mt-1">Manage your plan and invoices</p>
        </div>
        <UpgradeButton />
      </div>
      <BillingTierCard />
      <BudgetSettingsCard />
      <InvoicesList />
    </div>
  );
}
