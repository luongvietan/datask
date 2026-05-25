"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { setBudget, type BudgetOut } from "@/lib/api";

export function useSetBudget(authKey: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (params: { budget: number | null; threshold?: number }) =>
      setBudget(authKey, params.budget, params.threshold),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["usage"] });
      qc.invalidateQueries({ queryKey: ["budget"] });
    },
  });
}
