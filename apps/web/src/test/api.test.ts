import { describe, it, expect } from "vitest";
import { ApiError } from "@/lib/api";

describe("ApiError", () => {
  it("creates error with correct properties", () => {
    const err = new ApiError("quota_exceeded", "Quota exceeded", 402);
    expect(err.code).toBe("quota_exceeded");
    expect(err.status).toBe(402);
    expect(err.name).toBe("ApiError");
    expect(err.message).toBe("Quota exceeded");
  });

  it("is an instance of Error", () => {
    const err = new ApiError("rate_limited", "Rate limited", 429);
    expect(err instanceof Error).toBe(true);
  });
});
