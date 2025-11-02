'use client';

import {
    Checkbox,
    FormControl,
    FormControlLabel,
    InputLabel,
    MenuItem,
    Paper,
    Select,
    Stack,
    TextField,
} from '@mui/material';
import type {SelectChangeEvent} from '@mui/material/Select';

type ChunkingOptionsProps = {
    indexChunks: boolean;
    setIndexChunks: (value: boolean) => void;
    chunkingMode: 'sentence' | 'token';
    setChunkingMode: (value: 'sentence' | 'token') => void;
    sentencesPerChunk: number;
    setSentencesPerChunk: (value: number) => void;
    sentenceOverlap: number;
    setSentenceOverlap: (value: number) => void;
    tokensPerChunk: number;
    setTokensPerChunk: (value: number) => void;
    tokenOverlap: number;
    setTokenOverlap: (value: number) => void;
    chunkQueryMultiplier: number;
    setChunkQueryMultiplier: (value: number) => void;
};

export function ChunkingOptions({
    indexChunks,
    setIndexChunks,
    chunkingMode,
    setChunkingMode,
    sentencesPerChunk,
    setSentencesPerChunk,
    sentenceOverlap,
    setSentenceOverlap,
    tokensPerChunk,
    setTokensPerChunk,
    tokenOverlap,
    setTokenOverlap,
    chunkQueryMultiplier,
    setChunkQueryMultiplier,
}: ChunkingOptionsProps) {
    const handleChunkingModeChange = (event: SelectChangeEvent<'sentence' | 'token'>) => {
        setChunkingMode(event.target.value as 'sentence' | 'token');
    };

    return (
        <Paper variant="outlined" sx={{p: 2}}>
            <Stack spacing={2}>
                <FormControlLabel
                    control={<Checkbox checked={indexChunks} onChange={(event) => setIndexChunks(event.target.checked)} />}
                    label="Index chunks"
                />
                <Stack direction={{xs: 'column', sm: 'row'}} spacing={2}>
                    <FormControl sx={{minWidth: 160, flex: 1}} disabled={!indexChunks}>
                        <InputLabel id="chunking-mode-label">Mode</InputLabel>
                        <Select
                            labelId="chunking-mode-label"
                            value={chunkingMode}
                            label="Mode"
                            onChange={handleChunkingModeChange}
                        >
                            <MenuItem value="sentence">Sentence</MenuItem>
                            <MenuItem value="token">Token</MenuItem>
                        </Select>
                    </FormControl>
                    {chunkingMode === 'sentence' ? (
                        <>
                            <TextField
                                id="sentences-per-chunk"
                                name="sentencesPerChunk"
                                label="Sentences per chunk"
                                type="number"
                                value={sentencesPerChunk}
                                onChange={(event) => {
                                    const value = Number(event.target.value);
                                    setSentencesPerChunk(Number.isFinite(value) && value >= 1 ? value : 1);
                                }}
                                inputProps={{min: 1}}
                                autoComplete="off"
                                disabled={!indexChunks}
                                sx={{flex: 1}}
                            />
                            <TextField
                                id="sentence-overlap"
                                name="sentenceOverlap"
                                label="Sentence overlap"
                                type="number"
                                value={sentenceOverlap}
                                onChange={(event) => {
                                    const value = Number(event.target.value);
                                    setSentenceOverlap(Number.isFinite(value) && value >= 0 ? value : 0);
                                }}
                                inputProps={{min: 0}}
                                autoComplete="off"
                                disabled={!indexChunks}
                                sx={{flex: 1}}
                            />
                        </>
                    ) : (
                        <>
                            <TextField
                                id="tokens-per-chunk"
                                name="tokensPerChunk"
                                label="Tokens per chunk"
                                type="number"
                                value={tokensPerChunk}
                                onChange={(event) => {
                                    const value = Number(event.target.value);
                                    setTokensPerChunk(Number.isFinite(value) && value >= 10 ? value : 10);
                                }}
                                inputProps={{min: 10}}
                                autoComplete="off"
                                disabled={!indexChunks}
                                sx={{flex: 1}}
                            />
                            <TextField
                                id="token-overlap"
                                name="tokenOverlap"
                                label="Token overlap"
                                type="number"
                                value={tokenOverlap}
                                onChange={(event) => {
                                    const value = Number(event.target.value);
                                    setTokenOverlap(Number.isFinite(value) && value >= 0 ? value : 0);
                                }}
                                inputProps={{min: 0}}
                                autoComplete="off"
                                disabled={!indexChunks}
                                sx={{flex: 1}}
                            />
                        </>
                    )}
                </Stack>
                <TextField
                    id="chunk-query-multiplier"
                    name="chunkQueryMultiplier"
                    label="Query multiplier"
                    type="number"
                    value={chunkQueryMultiplier}
                    onChange={(event) => {
                        const value = Number(event.target.value);
                        setChunkQueryMultiplier(Number.isFinite(value) && value >= 1 ? value : 1);
                    }}
                    inputProps={{min: 1}}
                    autoComplete="off"
                    disabled={!indexChunks}
                    fullWidth
                />
            </Stack>
        </Paper>
    );
}
