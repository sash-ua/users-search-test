from typing import Any, Dict, List, TypedDict


class CollectionItem(TypedDict, total=False):
    embedding: List[float]
    metadata: Dict[str, Any]
    document: str

