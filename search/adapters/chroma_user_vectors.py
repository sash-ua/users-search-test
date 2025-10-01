from typing import Any, Dict, List

import chromadb
from chromadb.api.models.Collection import Collection

from search.models.collection_item import CollectionItem
from search.ports.user_vectors import Row, UserVectorRepository

def get_or_create_collection(
        persist_path: str,
        name: str,
        space: str = "cosine",
        force_recreate: bool = False,
        model: str | None = None,
        extra_meta: Dict[str, Any] | None = None,
) -> Collection:
    client = chromadb.PersistentClient(path=persist_path)
    if force_recreate:
        try:
            client.delete_collection(name)
        except Exception:
            pass
        md: Dict[str, Any] = {"hnsw:space": space, "model": model}
        if extra_meta:
            md.update(extra_meta)
        return client.create_collection(name=name, metadata=md)
    try:
        return client.get_collection(name)
    except Exception:
        md = {"hnsw:space": space, "model": model}
        if extra_meta:
            md.update(extra_meta)
        return client.create_collection(name=name, metadata=md)


class ChromaUserVectors(UserVectorRepository):
    def __init__(self, collection: Collection) -> None:
        self._col = collection

    @property
    def name(self) -> str:
        return self._col.name

    @property
    def metadata(self) -> Dict[str, Any] | None:
        try:
            return self._col.metadata
        except Exception:
            return None

    def upsert(
            self,
            ids: List[str],
            documents: List[str],
            vectors: List[List[float]],
            metadatas: List[Dict[str, Any]] | None = None,
    ) -> None:
        if not ids:
            return
        try:
            self._col.delete(ids=ids)
        except Exception:
            pass
        kwargs: Dict[str, Any] = {"ids": ids, "documents": documents, "embeddings": vectors}
        if metadatas is not None:
            kwargs["metadatas"] = metadatas
        self._col.add(**kwargs)

    def query(
            self, vector: List[float], k: int, where_document: str | None = None
    ) -> tuple[List[Row], List[float]]:
        if not vector:
            return [], []
        query_kwargs: Dict[str, Any] = {
            "query_embeddings": [vector],
            "n_results": max(1, k),
            "include": ["documents", "distances", "metadatas", "embeddings"],
        }
        if where_document:
            query_kwargs["where_document"] = {"$contains": where_document}
        res = self._col.query(**query_kwargs)
        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        dists = res.get("distances", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        rows: List[Row] = list(zip(ids, dists, docs, metas))
        return rows, dists

    def get_by_ids(self, ids: List[str], include_embeddings: bool = False) -> Dict[str, CollectionItem]:
        if not ids:
            return {}
        include: List[str] = ["metadatas"]
        if include_embeddings:
            include.append("embeddings")
        res = self._col.get(ids=ids, include=include)
        got_ids = res.get("ids")
        if got_ids is None:
            got_ids = []
        metas = res.get("metadatas")
        if metas is None:
            metas = []
        embs = res.get("embeddings")
        if embs is None:
            embs = []
        out: Dict[str, UserVectorRepository.Item] = {}
        for i, rid in enumerate(got_ids):
            item: UserVectorRepository.Item = {}
            if i < len(metas) and metas[i] is not None:
                item["metadata"] = metas[i]
            if include_embeddings and i < len(embs) and embs[i] is not None:
                item["embedding"] = embs[i]
            out[rid] = item
        return out
