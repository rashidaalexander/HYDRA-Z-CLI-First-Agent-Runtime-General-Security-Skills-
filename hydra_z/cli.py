from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

import typer

from . import __version__
from .core.schemas import Plan, Policy, Mode
from .core.io import read_json, read_yaml
from .core.executor import run_plan, replay
from .core.skills import load_skills

app = typer.Typer(add_completion=False, help="HYDRA Z — CLI-first agent runtime with skills, policy, telemetry, and replay.")

@app.command()
def version():
    typer.echo(__version__)

@app.command("skills")
def skills_list():
    skills = load_skills()
    rows = sorted(skills.values(), key=lambda s: s.name)
    for s in rows:
        typer.echo(f"{s.name:18}  risk={s.risk:6}  {s.description}")

@app.command()
def run(
    plan: Path = typer.Option(..., "--plan", "-p", exists=True, readable=True, help="Path to a JSON plan file"),
    policy: Path = typer.Option(Path("policies/default.yml"), "--policy", exists=True, readable=True, help="Policy YAML"),
    mode: Mode = typer.Option("shadow", "--mode", help="Execution mode: live | dry-run | shadow"),
    out: Path = typer.Option(Path("runs"), "--out", "-o", help="Output directory for run artifacts"),
):
    plan_obj = Plan.model_validate(read_json(plan))
    pol_obj = Policy.model_validate(read_yaml(policy))
    summary = run_plan(plan=plan_obj, policy=pol_obj, mode=mode, out_dir=out)
    typer.echo(f"Done: {summary['out_dir']}")
    typer.echo(f"Telemetry: {summary['telemetry_count']} events")
    typer.echo("Tip: use 'hydraz replay <run_dir>' to replay with a different mode.")

@app.command()
def replay_run(
    run_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="A previous run directory containing summary.json"),
    mode: Optional[Mode] = typer.Option(None, "--mode", help="Override mode for replay"),
):
    summary = replay(run_dir=run_dir, mode=mode)
    typer.echo(f"Replayed to: {summary['out_dir']}")
    typer.echo(f"Telemetry: {summary['telemetry_count']} events")

def main():
    app()

if __name__ == "__main__":
    main()
