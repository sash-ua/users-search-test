from typing import List

from openai import OpenAI

from search.ports.embeddings import EmbeddingsProvider


class OpenAIEmbeddings(EmbeddingsProvider):
    def __init__(self, client: OpenAI, model: str) -> None:
        self._client = client
        self._model = model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        resp = self._client.embeddings.create(
            model=self._model, input=texts, encoding_format="float"
        )
        return [d.embedding for d in resp.data]
