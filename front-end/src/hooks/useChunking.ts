import {useState} from 'react';

export function useChunking() {
    const [indexChunks, setIndexChunks] = useState(false);
    const [chunkingMode, setChunkingMode] = useState<'sentence' | 'token'>('sentence');
    const [sentencesPerChunk, setSentencesPerChunk] = useState(2);
    const [sentenceOverlap, setSentenceOverlap] = useState(1);
    const [tokensPerChunk, setTokensPerChunk] = useState(200);
    const [tokenOverlap, setTokenOverlap] = useState(50);
    const [chunkQueryMultiplier, setChunkQueryMultiplier] = useState(5);

    return {
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
    };
}
