import pytest

openai = pytest.importorskip("openai")

from search.adapters.openai_embeddings import OpenAIEmbeddings


class DummyResp:
    def __init__(self, vectors):
        self.data = [type("D", (), {"embedding": v}) for v in vectors]


class DummyClient:
    class embeddings:
        @staticmethod
        def create(model: str, input, encoding_format: str = "float"):
            texts = list(input)
            vecs = [[float(len(t))] for t in texts]
            return DummyResp(vecs)


def test_openai_embeddings_wraps_client():
    emb = OpenAIEmbeddings(DummyClient(), model="m")
    out = emb.embed_texts(["a", "abcd"])  # -> [[1.0], [4.0]]
    assert out == [[1.0], [4.0]]

