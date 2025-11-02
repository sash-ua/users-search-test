import {NextResponse} from 'next/server';
import type {NextRequest} from 'next/server';

export function middleware(request: NextRequest) {
  const url = new URL(request.url);
  const themeMode = url.searchParams.get('themeMode');
  const res = NextResponse.next();
  if (themeMode && ['light', 'dark', 'auto'].includes(themeMode)) {
    // Persist user-selected theme mode for SSR consistency
    res.cookies.set('themeMode', themeMode, {path: '/', maxAge: 60 * 60 * 24 * 365});
  }
  return res;
}

export const config = { matcher: ['/((?!api|_next/|.*\\..*).*)'] }
