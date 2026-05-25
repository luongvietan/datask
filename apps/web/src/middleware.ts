import { auth } from "@/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  const PROTECTED = ["/dashboard", "/playground", "/usage", "/keys", "/billing"];
  const isDashboard = PROTECTED.some((p) => req.nextUrl.pathname.startsWith(p));

  if (isDashboard && !isLoggedIn) {
    const loginUrl = new URL("/login", req.url);
    loginUrl.searchParams.set("callbackUrl", req.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/dashboard/:path*", "/playground", "/usage", "/keys", "/billing"],
};
