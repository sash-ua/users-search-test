import pytest

from search.utils.load_env import load_env


def test_load_env_reads_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.example.com")
    key, base = load_env()
    assert key == "sk-test"
    assert base == "https://api.example.com"


def test_load_env_raises_when_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    with pytest.raises(RuntimeError):
        load_env()

