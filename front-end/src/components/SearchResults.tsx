'use client';

import {useState} from 'react';
import {Alert, Box, Collapse, IconButton, Paper, Stack, Typography} from '@mui/material';
import {ExpandMore as ExpandMoreIcon} from '@mui/icons-material';
import type {SearchResponse} from '../hooks/useSearchForm';

type SearchResultsProps = {
    result: SearchResponse;
};

export function SearchResults({result}: SearchResultsProps) {
    const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

    const toggleExpanded = (id: string) => {
        setExpandedItems((prev) => {
            const next = new Set(prev);
            if (next.has(id)) {
                next.delete(id);
            } else {
                next.add(id);
            }
            return next;
        });
    };

    // Defensive guards: tolerate partial or malformed payloads
    const rows = Array.isArray((result as any)?.rows) ? result.rows : [];
    const safeCount = typeof result?.count === 'number' ? result.count : rows.length;

    return (
        <Paper variant="outlined" sx={{p: {xs: 2, sm: 3}}}>
            <Stack spacing={2}>
                <Typography variant="h5" component="h2">
                    Results ({safeCount})
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Collection: {result?.collection || 'n/a'} | Space: {result?.space || 'n/a'} | Model:{' '}
                    {result?.model || 'n/a'}
                </Typography>
                {result?.reindexed && (
                    <Alert severity="warning" variant="outlined">
                        Reindexed collection due to changed chunking/model settings.
                    </Alert>
                )}

                <Stack spacing={1.5}>
                    {rows.map((row) => {
                        const fullName = [row.metadata?.first_name, row.metadata?.last_name]
                            .filter(Boolean)
                            .join(' ');
                        const isExpanded = expandedItems.has(row.id);
                        const chunkText = row.metadata?.chunk_text;

                        return (
                            <Paper
                                key={row.id}
                                variant="outlined"
                                sx={{
                                    p: 2,
                                    transition: 'all 0.2s',
                                    '&:hover': {
                                        bgcolor: 'action.hover',
                                    },
                                    minHeight: 145
                                }}
                            >
                                <Stack spacing={1}>
                                    <Box
                                        sx={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}
                                    >
                                        <Typography
                                            variant="subtitle2"
                                            component="code"
                                            sx={{fontFamily: 'monospace', fontSize: '1rem'}}
                                        >
                                            {fullName}
                                        </Typography>
                                        <IconButton
                                            size="small"
                                            sx={{
                                                transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                                                transition: 'transform 0.3s',
                                                cursor: 'pointer',
                                            }}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                toggleExpanded(row.id);
                                            }}
                                        >
                                            <ExpandMoreIcon />
                                        </IconButton>
                                    </Box>
                                    <Typography variant="body2" color="text.secondary">
                                        dist {Number.isFinite(row.distance) ? row.distance.toFixed(6) : String(row.distance)}
                                        {typeof row.chunk_index === 'number' &&
                                        typeof row.chunk_count === 'number' ? (
                                            <Box component="span" sx={{ml: 0.5}}>
                                                (chunk {row.chunk_index + 1}/{row.chunk_count})
                                            </Box>
                                        ) : null}
                                    </Typography>
                                    {!isExpanded && row.snippet && (
                                        <Typography variant="body2" color="text.secondary" sx={{fontStyle: 'italic'}}>
                                            "{row.snippet}"
                                        </Typography>
                                    )}
                                    <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                                        <Box sx={{mt: 1, pt: 1, cursor: 'default',}}>
                                            {chunkText && (
                                                <Typography variant="body2" color="text.primary">
                                                    {chunkText}
                                                </Typography>
                                            )}
                                        </Box>
                                    </Collapse>
                                </Stack>
                            </Paper>
                        );
                    })}
                </Stack>
            </Stack>
        </Paper>
    );
}
