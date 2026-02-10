from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import uuid

from .schemas import Plan, Policy, Mode, now_iso
from .skills import load_skills
from .io import write_json, write_jsonl

def run_plan(*, plan: Plan, policy: Policy, mode: Mode, out_dir: Path) -> Dict[str, Any]:
    out_dir = out_dir / f"run_{uuid.uuid4().hex[:10]}"
    out_dir.mkdir(parents=True, exist_ok=True)

    skills = load_skills()

    telemetry: List[Dict[str, Any]] = []
    results: List[Dict[str, Any]] = []

    max_steps = min(policy.max_steps, 200)
    steps = plan.steps[:max_steps]

    ctx = {
        "mode": mode,
        "policy": policy.model_dump(),
        "out_dir": str(out_dir),
    }

    for i, step in enumerate(steps, start=1):
        ts = now_iso()
        skill_name = step.skill
        event = {
            "timestamp": ts,
            "step": i,
            "skill": skill_name,
            "mode": mode,
            "args": step.args,
            "outcome": "unknown",
            "error": None,
        }

        spec = skills.get(skill_name)
        if not spec:
            event["outcome"] = "error"
            event["error"] = "unknown_skill"
            telemetry.append(event)
            results.append({"skill": skill_name, "ok": False, "error": "unknown_skill"})
            continue

        try:
            out = spec.run(step.args, ctx)
            event["outcome"] = "ok" if out.get("ok", True) else "fail"
            results.append({"skill": skill_name, **out})
        except Exception as e:
            event["outcome"] = "error"
            event["error"] = str(e)
            results.append({"skill": skill_name, "ok": False, "error": str(e)})

        telemetry.append(event)

    summary = {
        "tool": "hydra-z",
        "plan": plan.model_dump(),
        "mode": mode,
        "policy": policy.model_dump(),
        "out_dir": str(out_dir),
        "results": results,
        "telemetry_count": len(telemetry),
    }

    write_json(out_dir / "summary.json", summary)
    write_jsonl(out_dir / "telemetry.jsonl", telemetry)
    return summary

def replay(*, run_dir: Path, mode: Mode | None = None) -> Dict[str, Any]:
    from .io import read_json
    from .schemas import Plan, Policy

    summ = read_json(run_dir / "summary.json")
    plan = Plan.model_validate(summ["plan"])
    pol = Policy.model_validate(summ["policy"])
    use_mode = mode or summ.get("mode", "shadow")
    out_parent = run_dir.parent / "replays"
    return run_plan(plan=plan, policy=pol, mode=use_mode, out_dir=out_parent)
