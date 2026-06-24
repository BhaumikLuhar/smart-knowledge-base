import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(
  request: NextRequest
) {
  const path =
    request.nextUrl.pathname;

  const publicRoutes = [
    "/login",
  ];

  const isPublic =
    publicRoutes.some(
      (route) =>
        path.startsWith(route)
    );

  if (isPublic) {
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/knowledge-base/:path*",
    "/users/:path*",
    "/settings/:path*",
    "/chat/:path*",
  ],
};