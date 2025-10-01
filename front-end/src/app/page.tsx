'use client';

import {FormEvent} from 'react';
import {Alert, Box, Container, Stack, Typography} from '@mui/material';
import {ThemeSwitcher} from '../components/ThemeSwitcher';
import {SearchForm} from '../components/SearchForm';
import {SearchResults} from '../components/SearchResults';
import {useSearchForm} from '../hooks/useSearchForm';
import {useChunking} from '../hooks/useChunking';
import {useDataset} from '../hooks/useDataset';

export default function Home() {
    const searchForm = useSearchForm();
    const chunking = useChunking();
    const dataset = useDataset(searchForm.BACKEND_URL);

    const {
        query,
        k,
        normalize,
        phrasePrefilter,
        threshold,
        model,
        setLoading,
        setResult,
        setError,
        loading,
        result,
        error,
        BACKEND_URL,
    } = searchForm;

    const {
        indexChunks,
        chunkingMode,
        sentencesPerChunk,
        sentenceOverlap,
        tokensPerChunk,
        tokenOverlap,
        chunkQueryMultiplier,
    } = chunking;

    async function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setError(null);
        setLoading(true);
        setResult(null);
        try {
            const dataPath = await dataset.handleUpload();
            const payload: Record<string, unknown> = {
                query,
                k,
                normalize,
                phrase_prefilter: phrasePrefilter,
                model,
            };
            if (indexChunks) {
                payload.index_chunks = true;
                payload.chunking_mode = chunkingMode;
                if (chunkingMode === 'sentence') {
                    payload.sentences_per_chunk = sentencesPerChunk;
                    payload.sentence_overlap = sentenceOverlap;
                } else {
                    payload.tokens_per_chunk = tokensPerChunk;
                    payload.token_overlap = tokenOverlap;
                }
                payload.chunk_query_multiplier = chunkQueryMultiplier;
            }
            if (threshold.trim()) payload.threshold = parseFloat(threshold);
            if (dataPath) payload.data = dataPath;

            const response = await fetch(`${BACKEND_URL}/search`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload),
            });

            const json = await response.json();
            if ((json as {error?: string}).error) throw new Error((json as {error: string}).error);
            setResult(json);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Request failed';
            setError(message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <Container maxWidth="md" sx={{py: 4}}>
            <Stack spacing={3}>
                <Box sx={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
                    <Box>
                        <Typography variant="h3" component="h1" fontWeight={600} gutterBottom>
                            Context Users Search
                        </Typography>
                        <Typography variant="body1" color="text.secondary">
                            Query your embeddings collection, optionally reindexing with custom chunking parameters.
                        </Typography>
                    </Box>
                    <ThemeSwitcher />
                </Box>

                <SearchForm
                    query={searchForm.query}
                    setQuery={searchForm.setQuery}
                    k={searchForm.k}
                    setK={searchForm.setK}
                    threshold={searchForm.threshold}
                    setThreshold={searchForm.setThreshold}
                    model={searchForm.model}
                    setModel={searchForm.setModel}
                    normalize={searchForm.normalize}
                    setNormalize={searchForm.setNormalize}
                    phrasePrefilter={searchForm.phrasePrefilter}
                    setPhrasePrefilter={searchForm.setPhrasePrefilter}
                    loading={searchForm.loading}
                    onSubmit={onSubmit}
                    chunkingProps={chunking}
                    datasetProps={dataset}
                />

                {error && (
                    <Alert severity="error" onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}

                {result && <SearchResults result={result} />}
            </Stack>
        </Container>
    );
}
