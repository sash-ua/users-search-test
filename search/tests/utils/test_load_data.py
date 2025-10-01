import json
from pathlib import Path

from search.utils.load_data import load_json


def test_load_json_reads_valid_file(tmp_path: Path):
    data = [{"a": 1}, {"b": 2}]
    p = tmp_path / "data.json"
    p.write_text(json.dumps(data))
    assert load_json(str(p)) == data


def test_load_json_missing_returns_empty(tmp_path: Path):
    p = tmp_path / "missing.json"
    assert load_json(str(p)) == []


def test_load_json_invalid_returns_empty(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("{ not valid json }")
    assert load_json(str(p)) == []

