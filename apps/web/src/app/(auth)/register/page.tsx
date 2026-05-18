import type { Metadata } from "next";
import { RegisterForm } from "@/components/ui/RegisterForm";

export const metadata: Metadata = { title: "Create account" };

export default function RegisterPage() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <span className="text-display-md text-ink font-medium tracking-tight">Datask</span>
        <p className="text-body text-ink-muted mt-2">500 free requests/month. No credit card.</p>
      </div>
      <RegisterForm />
      <p className="text-center text-caption text-ink-muted">
        Already have an account?{" "}
        <a href="/login" className="text-ink hover:underline">Sign in →</a>
      </p>
    </div>
  );
}
