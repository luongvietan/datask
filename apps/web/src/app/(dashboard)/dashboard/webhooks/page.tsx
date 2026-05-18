"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { useSessionKey } from "@/hooks/useSessionKey";

interface WebhookEndpoint {
  id: string;
  url: string;
  events: string;
  is_active: boolean;
  created_at: string;
}

function useWebhooks(apiKey: string | null) {
  return useQuery<WebhookEndpoint[]>({
    queryKey: ["webhooks", apiKey],
    queryFn: async () => {
      const res = await fetch("/api/v1/webhooks", {
        headers: { Authorization: `Bearer ${apiKey}` },
      });
      if (!res.ok) throw new Error("Failed to load webhooks");
      return res.json();
    },
    enabled: !!apiKey,
  });
}

export default function WebhooksPage() {
  const { data: sk } = useSessionKey();
  const sessionKey = sk?.session_key ?? null;
  const qc = useQueryClient();

  const { data: webhooks, isLoading } = useWebhooks(sessionKey);
  const [url, setUrl] = useState("");
  const [events, setEvents] = useState("*");
  const [showForm, setShowForm] = useState(false);
  const [newSecret, setNewSecret] = useState<string | null>(null);
  const [copiedSecret, setCopiedSecret] = useState(false);

  const createMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch("/api/v1/webhooks", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${sessionKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url, events }),
      });
      return res.json();
    },
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["webhooks"] });
      setNewSecret(data.secret);
      setShowForm(false);
      setUrl("");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await fetch(`/api/v1/webhooks/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${sessionKey}` },
      });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["webhooks"] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-display-sm text-ink">Webhooks</h2>
          <p className="text-body-sm text-ink-muted mt-1">
            Receive HTTP POST events when extractions complete.
          </p>
        </div>
        <Button variant="primary" onClick={() => setShowForm(true)} disabled={!sessionKey}>
          + Add endpoint
        </Button>
      </div>

      {newSecret && (
        <div className="rounded-xl border border-yellow-500/30 bg-yellow-500/10 p-4 space-y-3">
          <p className="text-body-sm text-yellow-400 font-medium">
            ⚠ Save your webhook secret — it will not be shown again.
          </p>
          <div className="flex items-center gap-2">
            <code className="flex-1 text-caption font-mono bg-surface-1 rounded-lg px-3 py-2 break-all text-ink">
              {newSecret}
            </code>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                navigator.clipboard.writeText(newSecret);
                setCopiedSecret(true);
                setTimeout(() => setCopiedSecret(false), 2000);
              }}
            >
              {copiedSecret ? "Copied!" : "Copy"}
            </Button>
          </div>
          <Button variant="ghost" size="sm" onClick={() => setNewSecret(null)}>Dismiss</Button>
        </div>
      )}

      {showForm && (
        <Card className="space-y-3">
          <p className="text-body-sm text-ink font-medium">New webhook endpoint</p>
          <Input
            placeholder="https://your-server.com/webhook"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <Input
            placeholder="Events (* for all, or: extract.completed, extract.failed)"
            value={events}
            onChange={(e) => setEvents(e.target.value)}
          />
          <div className="flex gap-2">
            <Button
              variant="primary"
              size="sm"
              loading={createMutation.isPending}
              onClick={() => createMutation.mutate()}
              disabled={!url.startsWith("http")}
            >
              Register
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setShowForm(false)}>
              Cancel
            </Button>
          </div>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(2)].map((_, i) => (
            <Card key={i} className="flex items-center gap-4">
              <Skeleton className="flex-1 h-12" />
            </Card>
          ))}
        </div>
      ) : webhooks && webhooks.length > 0 ? (
        <div className="space-y-3">
          {webhooks.map((webhook) => (
            <Card key={webhook.id} className="flex items-center justify-between gap-4">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant={webhook.is_active ? "success" : "error"}>
                    {webhook.is_active ? "active" : "inactive"}
                  </Badge>
                  <span className="text-caption text-ink-muted">
                    events: <code className="font-mono">{webhook.events}</code>
                  </span>
                </div>
                <p className="text-body-sm text-ink font-mono truncate">{webhook.url}</p>
                <p className="text-micro text-ink-muted mt-0.5">
                  Added {new Date(webhook.created_at).toLocaleDateString()}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="shrink-0 text-[#F87171] hover:text-[#F87171]"
                loading={deleteMutation.isPending}
                onClick={() => {
                  if (confirm("Delete this webhook endpoint?")) {
                    deleteMutation.mutate(webhook.id);
                  }
                }}
              >
                Delete
              </Button>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="text-center text-ink-muted text-body-sm py-8">
          No webhook endpoints yet. Add one to receive extraction events.
        </Card>
      )}

      <div className="rounded-xl bg-surface-1 border border-border p-4 space-y-2">
        <p className="text-caption text-ink font-medium">Signature verification</p>
        <p className="text-caption text-ink-muted">
          Each request includes an <code className="font-mono text-ink">X-Datask-Signature</code>{" "}
          header. Verify with HMAC-SHA256:
        </p>
        <pre className="text-caption font-mono text-green-400 bg-surface-2 rounded-lg px-4 py-3 overflow-auto">
{`import hmac, hashlib

def verify(secret, payload, signature):
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)`}
        </pre>
      </div>
    </div>
  );
}
