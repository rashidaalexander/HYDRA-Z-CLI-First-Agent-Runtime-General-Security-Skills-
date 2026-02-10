from __future__ import annotations
from typing import Any, Dict
import requests

from hydra_z.core.skills import SkillSpec
from hydra_z.core.policy import check_domain

def _run(args: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
    mode = ctx["mode"]
    url = str(args.get("url", ""))
    if not url:
        return {"ok": False, "error": "missing_url"}

    ok, reason = check_domain(url, ctx["policy"].get("allowlist_domains", []))
    if not ok:
        return {"ok": False, "error": reason}

    if mode in ("dry-run", "shadow"):
        return {"ok": True, "dry_run": True, "url": url, "status": None, "preview": "synthetic_response"}

    r = requests.get(url, timeout=20, headers={"User-Agent": "hydra-z/0.1"})
    return {"ok": True, "url": url, "status": r.status_code, "preview": r.text[:800]}

SKILL = SkillSpec(
    name="http.fetch",
    description="Fetch a URL (blocked unless allowlisted). No network in dry-run/shadow.",
    risk="medium",
    run=_run,
)
