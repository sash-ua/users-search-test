from typing import List, Protocol


class EmbeddingsProvider(Protocol):
    """Port for embedding text into vectors."""

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        ...
