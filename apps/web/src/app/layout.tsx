import type { Metadata, Viewport } from "next";
import { SessionProvider } from "next-auth/react";
import "./globals.css";
import { QueryProvider } from "@/components/providers/QueryProvider";

export const metadata: Metadata = {
  title: {
    default: "Datask — Web Data API for AI Agents",
    template: "%s | Datask",
  },
  description:
    "Ask for any web data. Get it structured. Native Cloudflare bypass, structured JSON output, and Natural Language extraction in one simple API.",
  keywords: [
    "web scraping API",
    "cloudflare bypass",
    "structured data extraction",
    "AI agents",
    "web data API",
    "firecrawl alternative",
  ],
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://datask.run",
    siteName: "Datask",
    title: "Datask — Web Data API for AI Agents",
    description: "Ask for any web data. Get it structured.",
  },
  twitter: {
    card: "summary_large_image",
    title: "Datask — Web Data API for AI Agents",
    description: "Ask for any web data. Get it structured.",
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: "#0C0C0C",
  colorScheme: "dark",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-canvas text-ink antialiased">
        <SessionProvider>
          <QueryProvider>{children}</QueryProvider>
        </SessionProvider>
      </body>
    </html>
  );
}
