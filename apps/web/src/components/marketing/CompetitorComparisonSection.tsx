import { Fragment } from "react";
import { HugeiconsIcon, type HugeiconsIconProps } from "@hugeicons/react";
import { ValidationIcon, AlertCircleIcon, StarIcon, CancelCircleIcon } from "@hugeicons/core-free-icons";

type IconProp = HugeiconsIconProps["icon"];

const COMPETITORS = ["Firecrawl", "Jina Reader", "Apify", "ScrapingBee", "Datask"];

type CellValue = "yes" | "no" | "partial" | "unique" | "note";

interface Row {
  feature: string;
  group: string;
  cells: { value: CellValue; note?: string }[];
  dataskNote?: string;
}

const ROWS: Row[] = [
  // Anti-bot
  {
    feature: "Cloudflare Bypass",
    group: "Anti-bot",
    cells: [
      { value: "partial", note: "Fails on many sites" },
      { value: "no" },
      { value: "partial", note: "Actor-based, manual" },
      { value: "partial", note: "Not Turnstile" },
      { value: "yes" },
    ],
    dataskNote: "Native engine",
  },
  {
    feature: "Turnstile Solve",
    group: "Anti-bot",
    cells: [
      { value: "no" },
      { value: "no" },
      { value: "partial", note: "Actor only" },
      { value: "no" },
      { value: "yes" },
    ],
    dataskNote: "Built-in, automatic",
  },
  {
    feature: "Adaptive Self-healing",
    group: "Anti-bot",
    cells: [
      { value: "no" },
      { value: "no" },
      { value: "no" },
      { value: "no" },
      { value: "unique" },
    ],
    dataskNote: "Only on market",
  },
  // Data output
  {
    feature: "Markdown Output",
    group: "Data output",
    cells: [
      { value: "yes" },
      { value: "yes" },
      { value: "partial", note: "Actor-dependent" },
      { value: "no" },
      { value: "yes" },
    ],
  },
  {
    feature: "Structured JSON",
    group: "Data output",
    cells: [
      { value: "partial", note: "+4 credits extra" },
      { value: "no" },
      { value: "yes" },
      { value: "no" },
      { value: "yes" },
    ],
    dataskNote: "Included",
  },
  {
    feature: "Natural Language → JSON",
    group: "Data output",
    cells: [
      { value: "no" },
      { value: "no" },
      { value: "no" },
      { value: "no" },
      { value: "unique" },
    ],
    dataskNote: "Only on market",
  },
  // Pricing
  {
    feature: "Usage-based pricing",
    group: "Pricing",
    cells: [
      { value: "no" },
      { value: "no" },
      { value: "partial", note: "Add-on only" },
      { value: "no" },
      { value: "yes" },
    ],
  },
  {
    feature: "Free tier",
    group: "Pricing",
    cells: [
      { value: "yes", note: "1K pages" },
      { value: "yes", note: "Generous" },
      { value: "yes", note: "$5 CU" },
      { value: "no" },
      { value: "yes", note: "500 req" },
    ],
  },
  {
    feature: "Entry price",
    group: "Pricing",
    cells: [
      { value: "note", note: "$16/mo" },
      { value: "note", note: "$0" },
      { value: "note", note: "$29/mo" },
      { value: "note", note: "$49/mo" },
      { value: "note", note: "$0.005/req" },
    ],
  },
];

function Cell({ value, note, isDatask }: { value: CellValue; note?: string; isDatask: boolean }) {
  if (value === "yes") {
    return (
      <td className={`py-3 text-center align-middle ${isDatask ? "bg-accent-blue/5" : ""}`}>
        <span className="inline-flex justify-center">
          <HugeiconsIcon icon={ValidationIcon as IconProp} size={16} strokeWidth={1.5} className="text-success-green" />
        </span>
      </td>
    );
  }
  if (value === "unique") {
    return (
      <td className={`py-3 text-center align-middle ${isDatask ? "bg-accent-blue/5" : ""}`}>
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-accent-blue/15 text-accent-blue text-[11px] font-medium whitespace-nowrap">
          <HugeiconsIcon icon={StarIcon as IconProp} size={11} strokeWidth={1.5} className="shrink-0" />
          Only one
        </span>
      </td>
    );
  }
  if (value === "partial") {
    return (
      <td className={`py-3 text-center align-middle ${isDatask ? "bg-accent-blue/5" : ""}`}>
        <span className="inline-flex justify-center">
          <HugeiconsIcon icon={AlertCircleIcon as IconProp} size={16} strokeWidth={1.5} className="text-[#F59E0B]" />
        </span>
        {note && (
          <p className="text-[10px] text-ink-muted mt-0.5 leading-tight">{note}</p>
        )}
      </td>
    );
  }
  if (value === "no") {
    return (
      <td className={`py-3 text-center align-middle ${isDatask ? "bg-accent-blue/5" : ""}`}>
        <span className="inline-flex justify-center opacity-25">
          <HugeiconsIcon icon={CancelCircleIcon as IconProp} size={16} strokeWidth={1.5} className="text-ink-muted" />
        </span>
      </td>
    );
  }
  // note
  return (
    <td className={`py-3 text-center align-middle ${isDatask ? "bg-accent-blue/5" : ""}`}>
      <span className={`text-body-sm font-medium ${isDatask ? "text-accent-blue" : "text-ink-muted"}`}>
        {note}
      </span>
    </td>
  );
}

// Pre-process rows to mark which ones start a new group
const PROCESSED_ROWS = ROWS.map((row, i) => ({
  ...row,
  showGroupHeader: i === 0 || row.group !== ROWS[i - 1].group,
}));

export function CompetitorComparisonSection() {
  return (
    <section className="bg-canvas py-24 border-t border-hairline-soft">
      <div className="container-app">
        <p className="text-caption text-ink-muted uppercase tracking-widest mb-4">Vs. the market</p>
        <h2 className="text-display-lg text-ink mb-4">
          The only tool in<br />the empty quadrant.
        </h2>
        <p className="text-body-lg text-ink-muted mb-14 max-w-[520px]">
          Strong anti-bot + low price + AI-native extraction. No competitor has all three.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-body-sm min-w-[640px]">
            <thead>
              <tr className="border-b border-hairline">
                <th className="text-left pb-4 font-medium text-ink-muted w-[200px]">Feature</th>
                {COMPETITORS.map((name, i) => (
                  <th
                    key={name}
                    className={`text-center pb-4 font-medium ${
                      i === COMPETITORS.length - 1
                        ? "text-accent-blue"
                        : "text-ink-muted"
                    }`}
                  >
                    {name}
                    {i === COMPETITORS.length - 1 && (
                      <span className="ml-1.5 inline-block w-1.5 h-1.5 rounded-full bg-success-green align-middle" />
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {PROCESSED_ROWS.map((row) => (
                <Fragment key={row.feature}>
                  {row.showGroupHeader && (
                    <tr>
                      <td
                        colSpan={COMPETITORS.length + 1}
                        className="pt-6 pb-2 text-caption text-ink-muted uppercase tracking-widest"
                      >
                        {row.group}
                      </td>
                    </tr>
                  )}
                  <tr className="border-b border-hairline-soft">
                    <td className="py-3 text-ink-muted">{row.feature}</td>
                    {row.cells.map((cell, i) => (
                      <Cell
                        key={COMPETITORS[i]}
                        value={cell.value}
                        note={cell.note}
                        isDatask={i === COMPETITORS.length - 1}
                      />
                    ))}
                  </tr>
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>

        {/* Callout strip */}
        <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-3">
          {[
            {
              label: "vs Firecrawl",
              text: "Firecrawl fails on Cloudflare Turnstile. Datask doesn't — and costs 3× less at low volume.",
            },
            {
              label: "vs Jina Reader",
              text: "Jina gives raw Markdown. Datask gives structured JSON with one API call, no extra LLM needed.",
            },
            {
              label: "vs Apify",
              text: "Apify is enterprise-complex. Datask is one HTTP request — no actors, no setup, no monthly seat.",
            },
          ].map(({ label, text }) => (
            <div key={label} className="bg-surface-1 rounded-xl p-5 border border-hairline">
              <p className="text-caption text-accent-blue font-medium mb-2">{label}</p>
              <p className="text-caption text-ink-muted leading-relaxed">{text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
