'use client';

import {useMemo, useState, useEffect, createContext, useContext, ReactNode} from 'react';
import {ThemeProvider as MuiThemeProvider, createTheme, useMediaQuery, CssBaseline} from '@mui/material';
import {usePathname, useRouter, useSearchParams} from 'next/navigation';
import {ThemeMode} from '../types/theme';

type ThemeModeContextType = {
    themeMode: ThemeMode;
    setThemeMode: (mode: ThemeMode) => void;
};

const ThemeModeContext = createContext<ThemeModeContextType>({
    themeMode: ThemeMode.Auto,
    setThemeMode: () => {},
});

export const useThemeMode = () => useContext(ThemeModeContext);

export function ThemeProvider({children}: {children: ReactNode}) {
    const router = useRouter();
    const pathname = usePathname();
    const searchParams = useSearchParams();
    const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)', {noSsr: true});
    const [themeMode, setThemeModeState] = useState<ThemeMode>(ThemeMode.Auto);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        const urlMode = searchParams?.get('themeMode');
        if (urlMode && Object.values(ThemeMode).includes(urlMode as ThemeMode)) {
            setThemeModeState(urlMode as ThemeMode);
            if (typeof window !== 'undefined') {
                localStorage.setItem('themeMode', urlMode);
            }
        } else if (typeof window !== 'undefined') {
            const stored = localStorage.getItem('themeMode');
            if (stored && Object.values(ThemeMode).includes(stored as ThemeMode)) {
                setThemeModeState(stored as ThemeMode);
            }
        }
    }, [searchParams]);

    const setThemeMode = (mode: ThemeMode) => {
        setThemeModeState(mode);
        if (typeof window !== 'undefined') {
            localStorage.setItem('themeMode', mode);
        }

        if (searchParams) {
            const params = new URLSearchParams(searchParams.toString());
            params.set('themeMode', mode);
            router.replace(`${pathname}?${params.toString()}`, {scroll: false});
        }
    };

    const actualMode = themeMode === ThemeMode.Auto ? (prefersDarkMode ? ThemeMode.Dark : ThemeMode.Light) : themeMode;

    const theme = useMemo(
        () =>
            createTheme({
                palette: {
                    mode: actualMode,
                },
            }),
        [actualMode],
    );

    return (
        <ThemeModeContext.Provider value={{themeMode, setThemeMode}}>
            <MuiThemeProvider theme={theme}>
                <CssBaseline />
                {children}
            </MuiThemeProvider>
        </ThemeModeContext.Provider>
    );
}
