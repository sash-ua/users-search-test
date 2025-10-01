import {useState, FormEvent} from 'react';

export type SearchResponse = {
    query: string;
    k: number;
    count: number;
    rows: {
        id: string;
        distance: number;
        metadata: Record<string, any>;
        snippet?: string | null;
        chunk_index?: number | null;
        chunk_count?: number | null;
    }[];
    distances: number[];
    collection?: string | null;
    space?: string | null;
    model?: string | null;
    reindexed?: boolean;
};

const BACKEND_URL = `${process.env.NEXT_PUBLIC_BACKEND_URL}${process.env.NEXT_PUBLIC_APP_PORT}`;

export function useSearchForm() {
    const [query, setQuery] = useState('');
    const [k, setK] = useState(5);
    const [normalize, setNormalize] = useState(true);
    const [phrasePrefilter, setPhrasePrefilter] = useState(true);
    const [threshold, setThreshold] = useState<string>('');
    const [model, setModel] = useState('text-embedding-qwen3-embedding-8b');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<SearchResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    return {
        query,
        setQuery,
        k,
        setK,
        normalize,
        setNormalize,
        phrasePrefilter,
        setPhrasePrefilter,
        threshold,
        setThreshold,
        model,
        setModel,
        loading,
        setLoading,
        result,
        setResult,
        error,
        setError,
        BACKEND_URL,
    };
}
