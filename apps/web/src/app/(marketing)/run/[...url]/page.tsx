/**
 * datask.run/run/{url} — Layer 1 viral endpoint.
 * Server component: fetches content from backend, renders Markdown.
 */
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { RunPageClient } from "./RunPageClient";

const DATASK_API_URL = process.env.DATASK_API_URL ?? "http://localhost:8000";

interface Props {
  params: Promise<{ url: string[] }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { url } = await params;
  const targetUrl = url.join("/");
  return {
    title: `Fetched: ${targetUrl}`,
    description: `Clean content from ${targetUrl} via Datask`,
  };
}

export default async function RunPage({ params }: Props) {
  const { url } = await params;

  // Reconstruct full URL (Next.js strips the leading https:/)
  const rawUrl = url.join("/");
  const targetUrl = rawUrl.startsWith("http") ? rawUrl : `https://${rawUrl}`;

  if (!targetUrl.startsWith("http://") && !targetUrl.startsWith("https://")) {
    notFound();
  }

  let content: string | null = null;
  let fetchError: string | null = null;
  let fetchedAt: string | null = null;

  try {
    const res = await fetch(
      `${DATASK_API_URL}/v1/fetch?url=${encodeURIComponent(targetUrl)}`,
      { next: { revalidate: 60 } }
    );

    if (res.ok) {
      const data = await res.json();
      content = data.content;
      fetchedAt = data.fetched_at;
    } else {
      const err = await res.json().catch(() => ({}));
      fetchError = err.message ?? `HTTP ${res.status}`;
    }
  } catch (err) {
    fetchError = "Failed to connect to Datask API.";
  }

  return (
    <RunPageClient
      targetUrl={targetUrl}
      content={content}
      fetchError={fetchError}
      fetchedAt={fetchedAt}
    />
  );
}
