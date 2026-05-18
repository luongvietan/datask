"use client";

import { Button } from "@/components/ui/Button";
import { useSessionKey } from "@/hooks/useSessionKey";
import { createCheckout } from "@/lib/api";
import { useState } from "react";

export function UpgradeButton() {
  const { data: sk } = useSessionKey();
  const [loading, setLoading] = useState(false);

  async function handleUpgrade() {
    if (!sk?.session_key) return;
    setLoading(true);
    try {
      const { checkout_url } = await createCheckout(sk.session_key);
      window.location.href = checkout_url;
    } catch (err) {
      console.error("Checkout failed:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Button variant="primary" onClick={handleUpgrade} loading={loading} disabled={!sk}>
      Upgrade plan
    </Button>
  );
}
