import type { Metadata } from "next";
import { PricingSection } from "@/components/marketing/PricingSection";
import { PricingComparisonTable } from "@/components/marketing/PricingComparisonTable";
import { FaqSection } from "@/components/marketing/FaqSection";

export const metadata: Metadata = {
  title: "Pricing",
  description:
    "Free tier, pay-as-you-go, and commit plans. Cheaper per successful request than any competitor.",
};

export default function PricingPage() {
  return (
    <>
      <PricingSection showFullPage />
      <PricingComparisonTable />
      <FaqSection />
    </>
  );
}
