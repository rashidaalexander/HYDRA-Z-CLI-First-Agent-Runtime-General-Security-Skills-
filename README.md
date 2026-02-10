# HYDRA Z — CLI-First Agent Runtime (General + Security Skills)

HYDRA Z is a **tool-like** agent runtime inspired by OpenClaw-style “skills”, but designed to scale:
- **Skill registry** (general + security tools)
- **Execution modes**: `live`, `dry-run`, `shadow`
- **Policy guardrails** (domain allowlists, workspace root, limits)
- **Telemetry** (JSONL) + **run summaries** (JSON)
- **Replay** of runs for debugging/research

**No HTML.** CLI only.

## Install
```bash
pip install .
```

## List skills
```bash
hydraz skills
```

## Run a plan (shadow mode by default)
```bash
hydraz run --plan plans/01_general_fetch.json --mode shadow
```

Artifacts:
- `runs/run_<id>/summary.json`
- `runs/run_<id>/telemetry.jsonl`

## Live mode (writes + network if allowlisted)
```bash
hydraz run --plan plans/01_general_fetch.json --mode live
```

## Security plans
Secrets scan (defensive):
```bash
hydraz run --plan plans/02_security_secrets.json --mode shadow
```

OSV dependency scan (defensive):
1) Create a `requirements.txt` in the repo root (or edit plan to point to your file)
2) Run in live mode:
```bash
hydraz run --plan plans/03_security_deps_osv.json --mode live
```

> In `dry-run` or `shadow`, HYDRA Z **skips network calls** (OSV + HTTP) and returns a safe placeholder.

## Replay a run
```bash
hydraz replay-run runs/run_<id> --mode shadow
```

## Extend with new skills
Add a file under `hydra_z/skills/` that defines `SKILL = SkillSpec(...)`.
That’s it.

## License
MIT
