"use client";

import { Button } from "@/components/ui/Button";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { ArrowUpRightStackIcon } from "@hugeicons/core-free-icons";
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
      <span className="inline-flex items-center gap-1.5">
        <Icon icon={ArrowUpRightStackIcon as IconProp} size={14} />
        Upgrade plan
      </span>
    </Button>
  );
}
