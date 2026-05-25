/**
 * Server-side route: lấy dashboard session key từ backend API.
 * Chỉ frontend authenticated mới gọi được.
 */
import { auth } from "@/auth";
import { NextResponse } from "next/server";

const DATASK_API_URL = process.env.DATASK_API_URL ?? "http://localhost:8000";

export async function GET() {
  const session = await auth();

  if (!session?.user?.accountId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const res = await fetch(`${DATASK_API_URL}/v1/auth/session-key`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ account_id: session.user.accountId }),
    cache: "no-store",
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    console.error(
      `[session-key] Backend ${res.status}: ${body}`,
    );
    return NextResponse.json({ error: "Failed to issue session key" }, { status: 500 });
  }

  const data = await res.json();
  return NextResponse.json(data);
}
