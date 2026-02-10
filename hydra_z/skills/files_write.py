from __future__ import annotations
from pathlib import Path
from typing import Any, Dict

from hydra_z.core.skills import SkillSpec
from hydra_z.core.policy import resolve_under_root

def _run(args: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
    mode = ctx["mode"]
    root = Path(ctx["policy"]["workspace_root"])
    path = Path(args.get("path", ""))
    content = str(args.get("content", ""))
    if not str(path):
        return {"ok": False, "error": "missing_path"}

    p = resolve_under_root(root, path)
    if mode in ("dry-run", "shadow"):
        return {"ok": True, "dry_run": True, "path": str(p), "bytes": len(content.encode('utf-8'))}

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {"ok": True, "path": str(p), "bytes": len(content.encode('utf-8'))}

SKILL = SkillSpec(
    name="files.write",
    description="Write a text file under workspace_root (no-op in dry-run/shadow).",
    risk="medium",
    run=_run,
)
