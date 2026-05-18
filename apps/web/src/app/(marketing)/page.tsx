import { HeroSection } from "@/components/marketing/HeroSection";
import { DemoSection } from "@/components/marketing/DemoSection";
import { FeaturesSection } from "@/components/marketing/FeaturesSection";
import { CodeExampleSection } from "@/components/marketing/CodeExampleSection";
import { PricingSection } from "@/components/marketing/PricingSection";
import { FaqSection } from "@/components/marketing/FaqSection";
import { CtaSection } from "@/components/marketing/CtaSection";

export default function LandingPage() {
  return (
    <>
      <HeroSection />
      <DemoSection />
      <FeaturesSection />
      <CodeExampleSection />
      <PricingSection />
      <FaqSection />
      <CtaSection />
    </>
  );
}
