'use client';

import {FormEvent} from 'react';
import {
    Box,
    Button,
    Checkbox,
    FormControlLabel,
    FormGroup,
    Paper,
    Stack,
    TextField,
} from '@mui/material';
import {ChunkingOptions} from './ChunkingOptions';
import {DatasetSelector} from './DatasetSelector';

type SearchFormProps = {
    query: string;
    setQuery: (value: string) => void;
    k: number;
    setK: (value: number) => void;
    threshold: string;
    setThreshold: (value: string) => void;
    model: string;
    setModel: (value: string) => void;
    normalize: boolean;
    setNormalize: (value: boolean) => void;
    phrasePrefilter: boolean;
    setPhrasePrefilter: (value: boolean) => void;
    loading: boolean;
    onSubmit: (event: FormEvent<HTMLFormElement>) => void;
    chunkingProps: any;
    datasetProps: any;
};

export function SearchForm({
    query,
    setQuery,
    k,
    setK,
    threshold,
    setThreshold,
    model,
    setModel,
    normalize,
    setNormalize,
    phrasePrefilter,
    setPhrasePrefilter,
    loading,
    onSubmit,
    chunkingProps,
    datasetProps,
}: SearchFormProps) {
    return (
        <Paper component="form" onSubmit={onSubmit} sx={{p: {xs: 2, sm: 3}}}>
            <Stack spacing={3}>
                <TextField
                    id="query-input"
                    name="query"
                    label="Query"
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="e.g. bicycle"
                    autoComplete="off"
                    spellCheck={false}
                    inputProps={{
                        'data-gramm': 'false',
                        'data-enable-grammarly': 'false',
                        'aria-autocomplete': 'none',
                    }}
                    fullWidth
                    required
                />

                <Stack direction={{xs: 'column', sm: 'row'}} spacing={2}>
                    <TextField
                        id="top-k"
                        name="k"
                        label="Top K"
                        type="number"
                        value={k}
                        onChange={(event) => {
                            const value = Number(event.target.value);
                            setK(Number.isFinite(value) && value >= 1 ? value : 1);
                        }}
                        inputProps={{min: 1}}
                        autoComplete="off"
                        fullWidth
                    />
                    <TextField
                        id="threshold"
                        name="threshold"
                        label="Threshold"
                        type="number"
                        value={threshold}
                        onChange={(event) => setThreshold(event.target.value)}
                        placeholder="optional"
                        autoComplete="off"
                        fullWidth
                    />
                    <TextField
                        id="model"
                        name="model"
                        label="Model"
                        value={model}
                        onChange={(event) => setModel(event.target.value)}
                        autoComplete="off"
                        fullWidth
                    />
                </Stack>

                <FormGroup row>
                    <FormControlLabel
                        control={<Checkbox checked={normalize} onChange={(event) => setNormalize(event.target.checked)} />}
                        label="Normalize"
                    />
                    <FormControlLabel
                        control={
                            <Checkbox
                                checked={phrasePrefilter}
                                onChange={(event) => setPhrasePrefilter(event.target.checked)}
                            />
                        }
                        label="Phrase prefilter"
                    />
                </FormGroup>

                <ChunkingOptions {...chunkingProps} />

                <DatasetSelector {...datasetProps} />

                <Box>
                    <Button type="submit" variant="contained" size="large" disabled={loading || !query.trim()}>
                        {loading ? 'Searching…' : 'Search'}
                    </Button>
                </Box>
            </Stack>
        </Paper>
    );
}
