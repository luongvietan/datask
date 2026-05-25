"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { Add01Icon, Alert01Icon } from "@hugeicons/core-free-icons";
import { useCreateKey } from "@/hooks/useApiKeys";
import { useSessionKey } from "@/hooks/useSessionKey";

export function CreateKeyButton() {
  const { data: sk } = useSessionKey();
  const sessionKey = sk?.session_key ?? "";
  const createMutation = useCreateKey(sessionKey);
  const [showForm, setShowForm] = useState(false);
  const [label, setLabel] = useState("");
  const [newKey, setNewKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function handleCreate() {
    if (!label.trim()) return;
    const result = await createMutation.mutateAsync(label.trim());
    setNewKey(result.key);
    setShowForm(false);
    setLabel("");
  }

  function copyKey() {
    if (!newKey) return;
    navigator.clipboard.writeText(newKey).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    });
  }

  if (newKey) {
    return (
      <div className="rounded-xl border border-yellow-500/30 bg-yellow-500/10 p-4 space-y-3">
        <p className="text-body-sm text-yellow-400 font-medium flex items-center gap-2">
          <Icon icon={Alert01Icon as IconProp} size={16} className="shrink-0" />
          Save your API key — it will not be shown again.
        </p>
        <div className="flex items-center gap-2">
          <code className="flex-1 text-caption font-mono bg-surface-1 rounded-lg px-3 py-2 overflow-x-auto text-ink break-all">
            {newKey}
          </code>
          <Button variant="secondary" size="sm" onClick={copyKey}>
            {copied ? "Copied!" : "Copy"}
          </Button>
        </div>
        <Button variant="ghost" size="sm" onClick={() => setNewKey(null)}>
          Dismiss
        </Button>
      </div>
    );
  }

  if (showForm) {
    return (
      <div className="flex items-center gap-2">
        <Input
          placeholder="Key label (e.g. production)"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCreate()}
          className="flex-1"
          autoFocus
        />
        <Button
          variant="primary"
          size="sm"
          onClick={handleCreate}
          loading={createMutation.isPending}
          disabled={!label.trim()}
        >
          Create
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            setShowForm(false);
            setLabel("");
          }}
        >
          Cancel
        </Button>
      </div>
    );
  }

  return (
    <Button variant="primary" onClick={() => setShowForm(true)} disabled={!sessionKey}>
      <span className="inline-flex items-center gap-1.5">
        <Icon icon={Add01Icon as IconProp} size={14} />
        New API key
      </span>
    </Button>
  );
}
