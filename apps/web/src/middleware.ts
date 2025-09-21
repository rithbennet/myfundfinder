import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const protectedPaths = ['/dashboard', '/profile', '/admin'];
  const isProtectedPath = protectedPaths.some(path => 
    request.nextUrl.pathname.startsWith(path)
  );

  if (isProtectedPath) {
    const authToken = request.cookies.get('auth-token');
    
    if (!authToken) {
      return NextResponse.redirect(new URL('/sign-in', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/profile/:path*', '/admin/:path*']
};
