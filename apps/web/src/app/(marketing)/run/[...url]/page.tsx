/**
 * Legacy path-based route: /run/https:/example.com/path
 * Reconstructs the URL and redirects to the canonical query-param format:
 * /run?url=https://example.com/path
 */
import { redirect } from "next/navigation";
import { notFound } from "next/navigation";

interface Props {
  params: Promise<{ url: string[] }>;
}

function reconstructUrl(segments: string[]): string | null {
  const raw = segments.join("/");
  const target = raw.startsWith("http")
    ? raw.replace(/^(https?:\/)([^/])/, "$1/$2")
    : `https://${raw}`;
  if (!target.startsWith("http://") && !target.startsWith("https://")) {
    return null;
  }
  return target;
}

export default async function RunLegacyPage({ params }: Props) {
  const { url } = await params;
  const targetUrl = reconstructUrl(url);

  if (!targetUrl) notFound();

  redirect(`/run?url=${encodeURIComponent(targetUrl)}`);
}
