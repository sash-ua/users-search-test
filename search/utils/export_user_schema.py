import json
from pathlib import Path

from search.models.user import User


def export_user_schema() -> None:
    schema = User.model_json_schema()
    out_dir = Path(__file__).resolve().parents[2] / "schemas"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "user.schema.json"
    out_file.write_text(json.dumps(schema, indent=2))
    print(f"Wrote schema to {out_file}")
