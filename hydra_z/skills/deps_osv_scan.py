from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json
import re
import requests

from hydra_z.core.skills import SkillSpec
from hydra_z.core.policy import resolve_under_root

OSV_QUERYBATCH_URL = "https://api.osv.dev/v1/querybatch"

def _parse_requirements(text: str) -> List[str]:
    pkgs = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name = re.split(r"[<>=!~]", line, maxsplit=1)[0].strip()
        if name:
            name = name.split("[", 1)[0].strip()
            if name:
                pkgs.append(name)
    return sorted(set(pkgs))

def _parse_package_lock(text: str) -> List[str]:
    data = json.loads(text)
    deps = data.get("dependencies", {}) or {}
    return sorted(set(deps.keys()))

def _parse_pyproject(text: str) -> List[str]:
    pkgs = set()
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("["):
            continue
        s = s.strip('"').strip("'")
        if any(op in s for op in ["<", ">", "=", "~"]):
            name = re.split(r"[<>=!~]", s, maxsplit=1)[0].strip()
            if name and " " not in name and len(name) <= 80:
                name = name.split("[", 1)[0].strip()
                if name:
                    pkgs.add(name)
    return sorted(pkgs)

def _detect(filename: str, text: str):
    fn = filename.lower()
    if fn.endswith("package-lock.json"):
        return "npm", _parse_package_lock(text)
    if fn.endswith("pyproject.toml"):
        return "PyPI", _parse_pyproject(text)
    # default
    return "PyPI", _parse_requirements(text)

def _query_batch(packages: List[str], ecosystem: str) -> List[Dict[str, Any]]:
    queries = [{"package": {"name": n, "ecosystem": ecosystem}} for n in packages]
    r = requests.post(OSV_QUERYBATCH_URL, json={"queries": queries}, timeout=40)
    r.raise_for_status()
    data = r.json()
    out = []
    for name, item in zip(packages, data.get("results", []) or []):
        vulns = (item or {}).get("vulns", []) or []
        out.append({
            "package": name,
            "ecosystem": ecosystem,
            "vuln_count": len(vulns),
            "vulnerabilities": [{"id": v.get("id"), "summary": v.get("summary"), "aliases": v.get("aliases", [])} for v in vulns[:20]],
        })
    return out

def _run(args: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
    mode = ctx["mode"]
    root = Path(ctx["policy"]["workspace_root"])
    path = Path(args.get("path", ""))
    if not str(path):
        return {"ok": False, "error": "missing_path"}
    p = resolve_under_root(root, path)
    text = p.read_text(encoding="utf-8", errors="replace")

    ecosystem, pkgs = _detect(p.name, text)
    if not pkgs:
        return {"ok": False, "error": "no_packages_detected", "ecosystem": ecosystem}

    if mode in ("dry-run", "shadow"):
        return {"ok": True, "dry_run": True, "ecosystem": ecosystem, "packages": pkgs[:50], "note": "OSV query skipped in dry-run/shadow"}

    results = _query_batch(pkgs, ecosystem)
    total = sum(r["vuln_count"] for r in results)
    return {"ok": True, "ecosystem": ecosystem, "packages_scanned": len(pkgs), "total_vulnerabilities": total, "results": results}

SKILL = SkillSpec(
    name="sec.osv_deps_scan",
    description="Scan dependency manifest via OSV (defensive). Skips network in dry-run/shadow.",
    risk="low",
    run=_run,
)
