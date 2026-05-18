import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Documentation",
  description: "Datask API reference, quickstart guides, and examples.",
};

export default function DocsPage() {
  return (
    <div className="container-app py-section">
      <h1 className="text-display-lg text-ink mb-8">Documentation</h1>
      {/* TODO: full docs in Phase 2 — link to /docs/openapi.json for now */}
      <p className="text-body-lg text-ink-muted">Coming soon. View live API spec at{" "}
        <a href="/openapi.json" className="text-accent-blue underline">/openapi.json</a>.
      </p>
    </div>
  );
}
