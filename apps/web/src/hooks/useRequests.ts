"use client";

import { useQuery } from "@tanstack/react-query";
import { listRequests } from "@/lib/api";
import type { RequestLogResponse } from "@/types";

interface UseRequestsParams {
  apiKey: string | null;
  limit?: number;
  offset?: number;
  layer?: number | null;
  success?: boolean | null;
}

export function useRequests({
  apiKey,
  limit = 50,
  offset = 0,
  layer = null,
  success = null,
}: UseRequestsParams) {
  return useQuery<RequestLogResponse, Error>({
    queryKey: ["requests", apiKey, { limit, offset, layer, success }],
    queryFn: () =>
      listRequests(apiKey!, { limit, offset, layer, success }),
    enabled: !!apiKey,
    staleTime: 30_000,
    retry: false,
  });
}
