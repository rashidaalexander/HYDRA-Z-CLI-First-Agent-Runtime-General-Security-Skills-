from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.parse import urlparse

from .schemas import Policy

def resolve_under_root(root: Path, target: Path) -> Path:
    root = root.resolve()
    target = (root / target).resolve() if not target.is_absolute() else target.resolve()
    if str(target).startswith(str(root)) is False:
        raise ValueError("path_outside_workspace_root")
    return target

def check_domain(url: str, allowlist: list[str]) -> Tuple[bool, str]:
    host = urlparse(url).hostname or ""
    if allowlist and host not in allowlist:
        return False, "domain_not_allowlisted"
    return True, "ok"
