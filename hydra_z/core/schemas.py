from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional
import time

Mode = Literal["live", "dry-run", "shadow"]

class Step(BaseModel):
    skill: str = Field(..., description="Skill name, e.g. deps.osv_scan")
    args: Dict[str, Any] = Field(default_factory=dict)

class Plan(BaseModel):
    name: str
    objective: str
    steps: List[Step]

class Policy(BaseModel):
    # Minimal-but-useful guardrails for v1.
    allowlist_domains: List[str] = Field(default_factory=list)
    workspace_root: str = Field(default=".", description="All file IO must stay under this root (live/dry-run/shadow).")
    max_file_bytes: int = 2_000_000
    max_steps: int = 25

def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")
