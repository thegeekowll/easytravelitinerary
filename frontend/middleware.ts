import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Get the path
  const path = request.nextUrl.pathname;

  // Define protected routes
  const isProtectedRoute = path.startsWith('/dashboard') || path.startsWith('/admin') || path.startsWith('/create-tour');
  
  // Define public routes (that might be inside protected areas, though usually not)
  // const isPublicRoute = path === '/dashboard/public-share'; // Example

  // Get the token from cookies
  const token = request.cookies.get('auth_token')?.value;

  // Redirect to login if accessing protected route without token
  if (isProtectedRoute && !token) {
    const url = new URL('/auth/login', request.url);
    // Add redirect param to return after login? 
    // For now, simpler is better.
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

// Config to match only specific paths
export const config = {
  matcher: [
    '/dashboard/:path*',
    '/admin/:path*',
    '/create-tour',
    '/create-tour/:path*',
  ],
};
