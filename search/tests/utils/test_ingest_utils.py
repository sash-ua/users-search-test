from types import SimpleNamespace

from search.utils.ingest import (
    normalize_text,
    hash_text,
    coerce_embedding,
    batched,
    safe_join_fields,
)


def test_normalize_text_keeps_case_and_punct():
    assert normalize_text("  Hello,   WORLD! ") == "Hello, WORLD!"


def test_hash_text_stable_on_whitespace():
    a = hash_text("A   B")
    b = hash_text("A B")
    assert a == b


def test_coerce_embedding_from_list_tuple_and_tolist():
    assert coerce_embedding([1, 2, 3]) == [1.0, 2.0, 3.0]
    assert coerce_embedding(("1", 2, 3.5)) == [1.0, 2.0, 3.5]
    obj = SimpleNamespace(tolist=lambda: [0.1, 0.2])
    assert coerce_embedding(obj) == [0.1, 0.2]
    assert coerce_embedding(None) == []


def test_batched_yields_chunks():
    seq = [str(i) for i in range(7)]
    out = list(batched(seq, 3))
    assert out == [["0", "1", "2"], ["3", "4", "5"], ["6"]]
    # Non-positive -> whole sequence
    assert list(batched(seq, 0)) == [seq]


def test_safe_join_fields_skips_empty_and_normalizes():
    s = safe_join_fields("  Hello ", None, "  world  ", "")
    assert s == "Hello world"

