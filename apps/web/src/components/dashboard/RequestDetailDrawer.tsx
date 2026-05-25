"use client";

import { useEffect } from "react";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import type { RequestLogItem } from "@/types";

interface RequestDetailDrawerProps {
  request: RequestLogItem | null;
  onClose: () => void;
}

export function RequestDetailDrawer({ request, onClose }: RequestDetailDrawerProps) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (request) {
      document.addEventListener("keydown", handleEsc);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEsc);
      document.body.style.overflow = "";
    };
  }, [request, onClose]);

  if (!request) return null;

  const formatTime = (iso: string | null) => {
    if (!iso) return "—";
    return new Date(iso).toLocaleString();
  };

  const formatLatency = (ms: number | null) => {
    if (ms == null) return "—";
    return `${ms}ms`;
  };

  return (
    <>
      <div
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
        aria-hidden="true"
      />
      <div className="fixed inset-y-0 right-0 w-full max-w-md bg-surface-1 shadow-xl z-50 overflow-y-auto">
        <div className="p-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-heading text-ink">Request Details</h2>
              {request.request_id && (
                <p className="text-micro text-ink-muted font-mono mt-1">
                  {request.request_id}
                </p>
              )}
            </div>
            <button
              onClick={onClose}
              className="text-ink-muted hover:text-ink transition-colors"
              aria-label="Close"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          <Card className="mb-4">
            <h3 className="text-body-sm text-ink mb-3">Overview</h3>
            <dl className="space-y-3">
              <div>
                <dt className="text-micro text-ink-muted">URL</dt>
                <dd className="text-caption text-ink font-mono break-all">{request.url}</dd>
              </div>
              {request.domain && (
                <div>
                  <dt className="text-micro text-ink-muted">Domain</dt>
                  <dd className="text-caption text-ink">{request.domain}</dd>
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <dt className="text-micro text-ink-muted">Layer</dt>
                  <dd className="text-caption text-ink">
                    <Badge variant="info">L{request.layer}</Badge>
                  </dd>
                </div>
                <div>
                  <dt className="text-micro text-ink-muted">Status</dt>
                  <dd className="text-caption text-ink">
                    <Badge variant={request.success ? "success" : "error"}>
                      {request.success ? "Success" : "Failed"}
                    </Badge>
                  </dd>
                </div>
                <div>
                  <dt className="text-micro text-ink-muted">Credits</dt>
                  <dd className="text-caption text-ink tabular-nums">{request.credits_used}</dd>
                </div>
                <div>
                  <dt className="text-micro text-ink-muted">Latency</dt>
                  <dd className="text-caption text-ink tabular-nums">{formatLatency(request.response_time_ms)}</dd>
                </div>
              </div>
              <div>
                <dt className="text-micro text-ink-muted">Timestamp</dt>
                <dd className="text-caption text-ink">{formatTime(request.created_at)}</dd>
              </div>
              {request.validation_valid != null && (
                <div>
                  <dt className="text-micro text-ink-muted">Validation</dt>
                  <dd className="text-caption text-ink">
                    <Badge variant={request.validation_valid ? "success" : "error"}>
                      {request.validation_valid ? "Valid" : "Invalid"}
                    </Badge>
                  </dd>
                </div>
              )}
            </dl>
          </Card>
        </div>
      </div>
    </>
  );
}
