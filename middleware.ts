// middleware.ts
import { clerkMiddleware } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

// Apply Clerk's middleware
export default clerkMiddleware((auth, req) => {
  return NextResponse.next()
})

// Apply to any routes you want to protect (e.g., all /dashboard pages)
export const config = {
  matcher: [
    '/((?!_next|static|favicon.ico).*)',
  ],
}
