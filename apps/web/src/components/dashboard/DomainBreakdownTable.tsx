import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

const MOCK = [
  { domain: "finance.yahoo.com", requests: 142, successRate: "98%" },
  { domain: "techcrunch.com", requests: 88, successRate: "100%" },
  { domain: "reuters.com", requests: 60, successRate: "95%" },
  { domain: "example-cf-site.com", requests: 52, successRate: "71%" },
];

export function DomainBreakdownTable() {
  return (
    <Card>
      <p className="text-body-sm text-ink mb-6">Top domains</p>
      <table className="w-full text-caption">
        <thead>
          <tr className="text-ink-muted border-b border-hairline-soft">
            <th className="text-left pb-3 font-medium">Domain</th>
            <th className="text-right pb-3 font-medium">Requests</th>
            <th className="text-right pb-3 font-medium">Success rate</th>
          </tr>
        </thead>
        <tbody>
          {MOCK.map((row) => (
            <tr key={row.domain} className="border-b border-hairline-soft last:border-0">
              <td className="py-3 text-ink font-mono">{row.domain}</td>
              <td className="py-3 text-right text-ink-muted tabular-nums">{row.requests}</td>
              <td className="py-3 text-right">
                <Badge variant={parseInt(row.successRate) >= 90 ? "success" : "warning"}>
                  {row.successRate}
                </Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}
