export interface SearchQueryArgs {
    query: string;
    k?: number;
    normalize?: boolean;
    phrase_prefilter?: boolean;
    threshold?: number | null;
    model?: string;
    data?: string;
    persist?: string;
    collection?: string;
    space?: string;
    index_chunks?: boolean;
    sentences_per_chunk?: number;
    sentence_overlap?: number;
    chunking_mode?: 'sentence' | 'token';
    tokens_per_chunk?: number;
    token_overlap?: number;
    chunk_query_multiplier?: number;
}