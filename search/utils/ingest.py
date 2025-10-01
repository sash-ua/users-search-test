from __future__ import annotations

import hashlib
import re
from typing import Any, Iterable, List, Optional, Sequence


def normalize_text(s: str | None) -> str:
    """Collapse whitespace and trim; keep punctuation/case for stable hashing."""
    if not s:
        return ""
    return re.sub(r"\s+", " ", s.strip())


def hash_text(s: str | None) -> str:
    """SHA-256 of normalized text to detect meaningful content changes."""
    return hashlib.sha256(normalize_text(s).encode("utf-8")).hexdigest()


def coerce_embedding(val: Any) -> List[float]:
    """Best-effort conversion of vectors to a list[float] without truthiness pitfalls.

    Accepts list/tuple/NumPy array-like. Returns [] on failure or None.
    """
    if val is None:
        return []
    if hasattr(val, "tolist"):
        try:
            out = val.tolist()
            return list(out) if isinstance(out, (list, tuple)) else list(out)  # type: ignore[arg-type]
        except Exception:
            return []
    if isinstance(val, (list, tuple)):
        try:
            return [float(x) for x in val]
        except Exception:
            return []
    return []


def batched(seq: Sequence[str], batch_size: int) -> Iterable[Sequence[str]]:
    """Yield slices of `seq` of size `batch_size`; non-positive yields whole seq once."""
    if batch_size <= 0:
        yield seq
        return
    n = len(seq)
    for i in range(0, n, batch_size):
        yield seq[i : i + batch_size]


def safe_join_fields(*fields: Optional[str]) -> str:
    """Join only non-empty, normalized values with single spaces."""
    return " ".join([normalize_text(f) for f in fields if f and normalize_text(f)])

