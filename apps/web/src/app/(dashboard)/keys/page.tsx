import type { Metadata } from "next";
import { ApiKeysList } from "@/components/dashboard/ApiKeysList";
import { CreateKeyButton } from "@/components/dashboard/CreateKeyButton";

export const metadata: Metadata = { title: "API Keys" };

export default function ApiKeysPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-display-md text-ink">API Keys</h1>
          <p className="text-body text-ink-muted mt-1">
            Keys are shown once at creation. Store them securely.
          </p>
        </div>
        <CreateKeyButton />
      </div>
      <ApiKeysList />
    </div>
  );
}
