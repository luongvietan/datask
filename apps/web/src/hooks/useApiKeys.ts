"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listKeys, createKey, revokeKey, type ApiKeyOut } from "@/lib/api";

export function useApiKeys(apiKey: string | null) {
  return useQuery<ApiKeyOut[]>({
    queryKey: ["keys", apiKey],
    queryFn: () => listKeys(apiKey!),
    enabled: !!apiKey,
    staleTime: 30_000,
  });
}

export function useCreateKey(authKey: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (label: string) => createKey(authKey, label),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["keys"] }),
  });
}

export function useRevokeKey(authKey: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (keyId: string) => revokeKey(authKey, keyId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["keys"] }),
  });
}
