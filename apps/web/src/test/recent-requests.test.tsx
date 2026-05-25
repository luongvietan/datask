import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

let mockSessionKey: string | null = "dtsk_sess_test";

vi.mock("@/hooks/useSessionKey", () => ({
  useSessionKey: () => ({ data: { session_key: mockSessionKey } }),
}));

let mockRequestsData: { requests: Array<unknown>; total: number } | undefined = undefined;
let mockRequestsLoading = true;
let mockRequestsError = false;

vi.mock("@/hooks/useRequests", () => ({
  useRequests: () => ({
    data: mockRequestsData,
    isLoading: mockRequestsLoading,
    isError: mockRequestsError,
  }),
}));

import { RecentRequestsTable } from "@/components/dashboard/RecentRequestsTable";

function renderTable() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <RecentRequestsTable />
    </QueryClientProvider>
  );
}

describe("RecentRequestsTable", () => {
  beforeEach(() => {
    mockSessionKey = "dtsk_sess_test";
    mockRequestsData = undefined;
    mockRequestsLoading = true;
    mockRequestsError = false;
  });

  it("renders title and subtitle", () => {
    renderTable();
    expect(screen.getByText("Recent requests")).toBeInTheDocument();
    expect(screen.getByText("Last 50 API calls")).toBeInTheDocument();
  });

  it("renders empty state when no requests", () => {
    mockRequestsLoading = false;
    mockRequestsData = { requests: [], total: 0 };
    renderTable();
    expect(screen.getByText(/no requests yet/i)).toBeInTheDocument();
  });

  it("renders error state on failure", () => {
    mockRequestsLoading = false;
    mockRequestsError = true;
    renderTable();
    expect(screen.getByText(/could not load requests/i)).toBeInTheDocument();
  });

  it("renders request rows when data is available", () => {
    mockRequestsLoading = false;
    mockRequestsData = {
      requests: [
        {
          request_id: "req_001",
          url: "https://example.com/page",
          domain: "example.com",
          layer: 2,
          success: true,
          credits_used: 1,
          response_time_ms: 120,
          validation_valid: true,
          created_at: "2026-05-25T10:00:00Z",
        },
      ],
      total: 1,
    };
    renderTable();
    expect(screen.getByText("https://example.com/page")).toBeInTheDocument();
    expect(screen.getByText("L2")).toBeInTheDocument();
  });
});
