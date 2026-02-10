from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import re

from hydra_z.core.skills import SkillSpec
from hydra_z.core.policy import resolve_under_root

_PATTERNS = [
    ("AWS_ACCESS_KEY_ID", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS_SECRET_ACCESS_KEY", re.compile(r"(?i)aws(.{0,20})?(secret|private).{0,20}['\"]?[0-9a-zA-Z/+]{40}['\"]?")),
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    ("SLACK_TOKEN", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,48}")),
    ("GITHUB_TOKEN", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,255}")),
]

def _scan_file(path: Path, max_bytes: int) -> List[Dict[str, Any]]:
    data = path.read_bytes()
    if len(data) > max_bytes:
        return [{"path": str(path), "rule": "SKIPPED_TOO_LARGE", "match": None}]
    text = data.decode("utf-8", errors="replace")
    hits = []
    for name, rx in _PATTERNS:
        for m in rx.finditer(text):
            snippet = text[max(0, m.start()-30): m.end()+30]
            hits.append({"path": str(path), "rule": name, "snippet": snippet})
    return hits

def _run(args: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
    root = Path(ctx["policy"]["workspace_root"])
    target = Path(args.get("path", "."))
    p = resolve_under_root(root, target)
    max_bytes = int(ctx["policy"]["max_file_bytes"])
    include = args.get("include", [".py", ".txt", ".env", ".json", ".yml", ".yaml", ".toml", ".md"])
    include = set(include)

    files = []
    if p.is_file():
        files = [p]
    else:
        for fp in p.rglob("*"):
            if fp.is_file() and (fp.suffix in include or fp.name in {".env"}):
                files.append(fp)

    hits = []
    for fp in files[:2000]:
        hits.extend(_scan_file(fp, max_bytes))

    return {"ok": True, "target": str(p), "files_scanned": len(files), "hits": hits, "hit_count": len([h for h in hits if h.get("match") is None and h.get("rule","").startswith("SKIPPED")]) and 0 or len([h for h in hits if h.get("rule") and not h.get("rule","").startswith("SKIPPED")])}

SKILL = SkillSpec(
    name="sec.secrets_scan",
    description="Scan files for common secret patterns (defensive).",
    risk="low",
    run=_run,
)
