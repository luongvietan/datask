"use client";

import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { Copy01Icon, Tick01Icon } from "@hugeicons/core-free-icons";
import { useApiKeys, useRevokeKey } from "@/hooks/useApiKeys";
import { useSessionKey } from "@/hooks/useSessionKey";

export function ApiKeysList() {
  const { data: sk } = useSessionKey();
  const sessionKey = sk?.session_key ?? null;
  const { data: keys, isLoading, error } = useApiKeys(sessionKey);
  const revokeMutation = useRevokeKey(sessionKey ?? "");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(2)].map((_, i) => (
          <Card key={i} className="flex items-center justify-between gap-4">
            <div className="space-y-2 flex-1">
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-3 w-56" />
            </div>
            <Skeleton className="h-8 w-16" />
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Card className="text-center text-ink-muted text-body-sm py-8">
        Failed to load API keys.
      </Card>
    );
  }

  if (!keys || keys.length === 0) {
    return (
      <Card className="text-center text-ink-muted text-body-sm py-8">
        No API keys yet. Create your first key above.
      </Card>
    );
  }

  function copyToClipboard(text: string, keyId: string) {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedId(keyId);
      setTimeout(() => setCopiedId(null), 2000);
    });
  }

  return (
    <div className="space-y-3">
      {keys.map((key) => (
        <Card key={key.id} className="flex items-center justify-between gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-body-sm text-ink">{key.label}</span>
              <Badge variant={key.is_active ? "success" : "error"}>
                {key.is_active ? "active" : "revoked"}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <code className="text-caption text-ink-muted font-mono">
                {key.key_preview}
              </code>
              <button
                onClick={() => copyToClipboard(key.key_preview, key.id)}
                className="text-ink-muted hover:text-ink transition-colors"
                title="Copy prefix"
              >
                {copiedId === key.id ? (
                  <Icon icon={Tick01Icon as IconProp} size={14} className="text-success-green" />
                ) : (
                  <Icon icon={Copy01Icon as IconProp} size={14} />
                )}
              </button>
            </div>
            <p className="text-micro text-ink-muted mt-0.5">
              Created {new Date(key.created_at).toLocaleDateString()}
            </p>
          </div>

          {key.is_active && (
            <Button
              variant="ghost"
              size="sm"
              className="shrink-0 text-[#F87171] hover:text-[#F87171]"
              loading={revokeMutation.isPending}
              onClick={() => {
                if (confirm(`Revoke key "${key.label}"? This cannot be undone.`)) {
                  revokeMutation.mutate(key.id);
                }
              }}
            >
              Revoke
            </Button>
          )}
        </Card>
      ))}
    </div>
  );
}
