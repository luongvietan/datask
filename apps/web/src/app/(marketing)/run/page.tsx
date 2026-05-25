import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { RunPageClient } from "./[...url]/RunPageClient";

interface Props {
  searchParams: Promise<{ url?: string }>;
}

export async function generateMetadata({ searchParams }: Props): Promise<Metadata> {
  const { url } = await searchParams;
  return {
    title: url ? `Fetching: ${url}` : "Run — Datask",
    description: url ? `Clean content from ${url} via Datask` : "Fetch any URL with Datask",
  };
}

export default async function RunPage({ searchParams }: Props) {
  const { url } = await searchParams;

  if (!url || (!url.startsWith("http://") && !url.startsWith("https://"))) {
    notFound();
  }

  return <RunPageClient targetUrl={url} />;
}
