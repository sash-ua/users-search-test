'use client';

import {IconButton, Tooltip} from '@mui/material';
import {Brightness4, Brightness7, BrightnessAuto} from '@mui/icons-material';
import {useThemeMode} from '../providers/ThemeProvider';
import {ThemeMode} from '../types/theme';

export function ThemeSwitcher() {
    const {themeMode, setThemeMode} = useThemeMode();

    const cycleTheme = () => {
        const modes = [ThemeMode.Auto, ThemeMode.Light, ThemeMode.Dark];
        const currentIndex = modes.indexOf(themeMode);
        const nextIndex = (currentIndex + 1) % modes.length;
        setThemeMode(modes[nextIndex]);
    };

    const themeIcon = themeMode === ThemeMode.Auto ? <BrightnessAuto /> : themeMode === ThemeMode.Light ? <Brightness7 /> : <Brightness4 />;
    const themeLabel = themeMode === ThemeMode.Auto ? 'Auto' : themeMode === ThemeMode.Light ? 'Light' : 'Dark';

    return (
        <Tooltip title={`Theme: ${themeLabel}`}>
            <IconButton onClick={cycleTheme} size="large" sx={{ml: 2}}>
                {themeIcon}
            </IconButton>
        </Tooltip>
    );
}
