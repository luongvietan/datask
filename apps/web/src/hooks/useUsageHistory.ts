"use client";

import { useQuery } from "@tanstack/react-query";

interface DayData {
  date: string;
  requests: number;
  successful: number;
}

interface UsageHistoryData {
  history: DayData[];
}

export function useUsageHistory(apiKey: string | null) {
  return useQuery<UsageHistoryData, Error>({
    queryKey: ["usage-history", apiKey],
    queryFn: async () => {
      const res = await fetch("/api/v1/billing/history", {
        headers: { Authorization: `Bearer ${apiKey}` },
      });
      if (!res.ok) throw new Error("Failed to load history");
      return res.json();
    },
    enabled: !!apiKey,
    staleTime: 60_000,
  });
}

export function useTopDomains(apiKey: string | null) {
  return useQuery<{ domains: { domain: string; count: number }[] }, Error>({
    queryKey: ["top-domains", apiKey],
    queryFn: async () => {
      const res = await fetch("/api/v1/billing/domains", {
        headers: { Authorization: `Bearer ${apiKey}` },
      });
      if (!res.ok) throw new Error("Failed to load domains");
      return res.json();
    },
    enabled: !!apiKey,
    staleTime: 60_000,
  });
}
