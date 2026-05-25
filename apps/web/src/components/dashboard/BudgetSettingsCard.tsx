"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { InformationCircleIcon, Tick02Icon } from "@hugeicons/core-free-icons";
import { useSessionKey } from "@/hooks/useSessionKey";
import { useUsage } from "@/hooks/useUsage";
import { useSetBudget } from "@/hooks/useBudget";

const PRESETS = [1000, 2500, 5000, 10000, 25000];

export function BudgetSettingsCard() {
  const { data: sk } = useSessionKey();
  const { data: usage } = useUsage(sk?.session_key ?? null);
  const setBudgetMutation = useSetBudget(sk?.session_key ?? "");

  const [budgetInput, setBudgetInput] = useState("");
  const [threshold, setThreshold] = useState(80);
  const [saved, setSaved] = useState(false);

  const isPayg = usage?.tier !== "free";
  const currentBudget = usage?.budget ?? null;

  useEffect(() => {
    if (currentBudget !== null) {
      setBudgetInput(String(currentBudget));
    }
  }, [currentBudget]);

  useEffect(() => {
    if (usage?.alert_threshold !== undefined) {
      setThreshold(usage.alert_threshold);
    }
  }, [usage?.alert_threshold]);

  if (!isPayg) return null;

  const handleSave = () => {
    const val = budgetInput.trim();
    const budget = val === "" || val === "0" ? null : parseInt(val, 10);
    if (budget !== null && (isNaN(budget) || budget < 0)) return;

    setBudgetMutation.mutate(
      { budget, threshold },
      {
        onSuccess: () => {
          setSaved(true);
          setTimeout(() => setSaved(false), 2000);
        },
      }
    );
  };

  const handleClearBudget = () => {
    setBudgetInput("");
    setBudgetMutation.mutate({ budget: null, threshold });
  };

  return (
    <Card variant="default" className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-headline text-ink">Monthly Budget Cap</span>
        <span className="text-caption text-ink-muted flex items-center gap-1" title="Set a monthly credit limit. Requests will be blocked (429) when exceeded.">
          <Icon icon={InformationCircleIcon as IconProp} size={14} />
        </span>
      </div>

      <div className="space-y-3">
        <div>
          <label className="text-caption text-ink-muted block mb-1">
            Monthly credit budget (leave empty for unlimited)
          </label>
          <div className="flex gap-2 flex-wrap">
            {PRESETS.map((p) => (
              <button
                key={p}
                onClick={() => setBudgetInput(String(p))}
                className={`px-3 py-1 rounded-lg text-caption border transition-colors ${
                  budgetInput === String(p)
                    ? "border-[#0099FF] bg-[#0099FF]/10 text-[#0099FF]"
                    : "border-surface-2 text-ink-muted hover:border-surface-3"
                }`}
              >
                {p.toLocaleString()}
              </button>
            ))}
          </div>
          <input
            type="number"
            min={0}
            value={budgetInput}
            onChange={(e) => setBudgetInput(e.target.value)}
            placeholder="Unlimited"
            className="mt-2 w-full rounded-lg bg-surface-2 border border-surface-2 px-3 py-2 text-body text-ink placeholder:text-ink-muted/50 focus:outline-none focus:border-[#0099FF] transition-colors"
          />
        </div>

        <div>
          <label className="text-caption text-ink-muted block mb-1">
            Alert threshold: {threshold}%
          </label>
          <input
            type="range"
            min={10}
            max={100}
            step={10}
            value={threshold}
            onChange={(e) => setThreshold(parseInt(e.target.value, 10))}
            className="w-full accent-[#0099FF]"
          />
        </div>

        <div className="flex gap-2">
          <Button
            onClick={handleSave}
            disabled={setBudgetMutation.isPending}
            className="flex items-center gap-1.5"
          >
            {saved ? (
              <>
                <Icon icon={Tick02Icon as IconProp} size={14} />
                Saved
              </>
            ) : setBudgetMutation.isPending ? (
              "Saving..."
            ) : (
              "Save budget"
            )}
          </Button>
          {currentBudget !== null && (
            <button
              onClick={handleClearBudget}
              className="text-caption text-ink-muted hover:text-[#0099FF] transition-colors px-3 py-1"
            >
              Remove cap
            </button>
          )}
        </div>
      </div>

      {setBudgetMutation.isError && (
        <p className="text-caption text-[#EF4444]">
          Failed to save budget. Please try again.
        </p>
      )}
    </Card>
  );
}
