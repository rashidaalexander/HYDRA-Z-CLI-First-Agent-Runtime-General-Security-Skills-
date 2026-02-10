from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import json
import yaml

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(read_text(path))

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def read_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(read_text(path)) or {}

def write_yaml(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(obj, sort_keys=False), encoding="utf-8")
