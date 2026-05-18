"use client";

import { useQuery } from "@tanstack/react-query";
import { getUsage, type UsageSummaryOut } from "@/lib/api";

export function useUsage(apiKey: string | null) {
  return useQuery<UsageSummaryOut>({
    queryKey: ["usage", apiKey],
    queryFn: () => getUsage(apiKey!),
    enabled: !!apiKey,
    staleTime: 60_000,  // refresh every 60s
    retry: false,
  });
}
