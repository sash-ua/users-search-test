import {cookies} from 'next/headers';
import {ThemeProvider} from './ThemeProvider';
import {ThemeMode} from '../types/theme';
import React from 'react';

export function ThemeServerProvider({children}: {children: React.ReactNode}) {
    const cookieStore = cookies();
    const cookieMode = cookieStore.get('themeMode')?.value as ThemeMode | undefined;
    const initialMode: ThemeMode = cookieMode === ThemeMode.Dark || cookieMode === ThemeMode.Light
        ? cookieMode
        : ThemeMode.Light;
    return <ThemeProvider initialMode={initialMode}>{children}</ThemeProvider>;
}

