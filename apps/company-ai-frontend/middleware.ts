import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const token = request.cookies.get("auth_token")?.value || 
                request.headers.get("authorization")?.replace("Bearer ", "")

  // Public routes
  const publicRoutes = ["/login"]
  const isPublicRoute = publicRoutes.some(route => 
    request.nextUrl.pathname === route
  )

  // If accessing login page and already authenticated, redirect to chat
  if (request.nextUrl.pathname === "/login" && token) {
    return NextResponse.redirect(new URL("/chat", request.url))
  }

  // If accessing protected route without token, redirect to login
  if (!isPublicRoute && !token) {
    // Check localStorage (client-side only)
    // For server-side, we'll rely on the client-side redirect
    return NextResponse.next()
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
}
