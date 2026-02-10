from __future__ import annotations
from pathlib import Path
from typing import Any, Dict

from hydra_z.core.skills import SkillSpec
from hydra_z.core.policy import resolve_under_root

def _run(args: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
    root = Path(ctx["policy"]["workspace_root"])
    path = Path(args.get("path", ""))
    if not str(path):
        return {"ok": False, "error": "missing_path"}
    p = resolve_under_root(root, path)
    max_bytes = int(ctx["policy"]["max_file_bytes"])
    data = p.read_bytes()
    if len(data) > max_bytes:
        return {"ok": False, "error": "file_too_large", "bytes": len(data), "max_bytes": max_bytes}
    text = data.decode("utf-8", errors="replace")
    return {"ok": True, "path": str(p), "preview": text[:600], "bytes": len(data)}

SKILL = SkillSpec(
    name="files.read",
    description="Read a file under workspace_root with size limits.",
    risk="low",
    run=_run,
)
