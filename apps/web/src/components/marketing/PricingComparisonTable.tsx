export function PricingComparisonTable() {
  const rows = [
    { feature: "Cloudflare bypass", free: true, payg: true, commit: true },
    { feature: "Layer 1 — Fetch", free: true, payg: true, commit: true },
    { feature: "Layer 2 — Schema extract", free: true, payg: true, commit: true },
    { feature: "Layer 3 — NL Prompt", free: false, payg: false, commit: true },
    { feature: "Webhooks", free: false, payg: false, commit: true },
    { feature: "MCP Server", free: false, payg: true, commit: true },
    { feature: "Priority support", free: false, payg: false, commit: true },
    { feature: "SLA guarantee", free: false, payg: false, commit: true },
  ];

  return (
    <section className="bg-canvas py-16 border-t border-hairline-soft">
      <div className="container-app max-w-[800px]">
        <h2 className="text-display-md text-ink mb-8">Feature comparison</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-body-sm">
            <thead>
              <tr className="border-b border-hairline text-ink-muted">
                <th className="text-left pb-3 font-medium">Feature</th>
                <th className="text-center pb-3 font-medium">Free</th>
                <th className="text-center pb-3 font-medium">PAYG</th>
                <th className="text-center pb-3 font-medium">Commit</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.feature} className="border-b border-hairline-soft">
                  <td className="py-3 text-ink-muted">{row.feature}</td>
                  {(["free", "payg", "commit"] as const).map((tier) => (
                    <td key={tier} className="py-3 text-center">
                      {row[tier] ? (
                        <span className="text-success-green">✓</span>
                      ) : (
                        <span className="text-ink-muted opacity-30">—</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
