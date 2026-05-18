import type { Metadata } from "next";
import { LoginForm } from "@/components/ui/LoginForm";

export const metadata: Metadata = { title: "Sign in" };

export default function LoginPage() {
  return (
    <div className="space-y-8">
      {/* Wordmark */}
      <div className="text-center">
        <span className="text-display-md text-ink font-medium tracking-tight">Datask</span>
      </div>
      <LoginForm />
      <p className="text-center text-caption text-ink-muted">
        No account?{" "}
        <a href="/register" className="text-ink hover:underline">
          Get started for free →
        </a>
      </p>
    </div>
  );
}
