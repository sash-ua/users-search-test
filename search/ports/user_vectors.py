from typing import Any, Dict, List, Protocol, Tuple

from search.models.collection_item import CollectionItem

Row = Tuple[str, float, str, Dict[str, Any]]


class UserVectorRepository(Protocol):
    """Port for persisting and querying user vectors."""

    def upsert(
            self,
            ids: List[str],
            documents: List[str],
            vectors: List[List[float]],
            metadatas: List[Dict[str, Any]] | None = None,
    ) -> None:
        ...

    def query(
        self, vector: List[float], k: int, where_document: str | None = None
    ) -> tuple[List[Row], List[float]]:
        ...

    def get_by_ids(
        self, ids: List[str], include_embeddings: bool = False
    ) -> Dict[str, CollectionItem]:
        """Return mapping from id to stored data (embedding/metadata/document if available)."""
        ...
