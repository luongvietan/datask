import { Card } from "@/components/ui/Card";

export function InvoicesList() {
  return (
    <Card>
      <p className="text-body-sm text-ink mb-4">Invoices</p>
      <p className="text-caption text-ink-muted">No invoices yet. Invoices appear here after upgrading.</p>
    </Card>
  );
}
