"use client";

import { useQuery } from "@tanstack/react-query";

interface SessionKeyData {
  session_key: string;
  expires_in: number;
}

export function useSessionKey() {
  return useQuery<SessionKeyData, Error>({
    queryKey: ["session-key"],
    queryFn: async () => {
      const res = await fetch("/api/session-key");
      if (!res.ok) {
        throw new Error("Failed to get session key");
      }
      return res.json();
    },
    staleTime: 1000 * 60 * 60, // 1h
    retry: 2,
  });
}
