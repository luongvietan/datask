"use client";

import { Input } from "./Input";
import { Button } from "./Button";
import { Card } from "./Card";

export function RegisterForm() {
  return (
    <Card className="space-y-5">
      <Input label="Email" type="email" placeholder="you@company.com" />
      <Button variant="primary" className="w-full justify-center">
        Create free account →
      </Button>
      <p className="text-micro text-ink-muted text-center">
        We&apos;ll send a verification link. No credit card required.
      </p>
    </Card>
  );
}
