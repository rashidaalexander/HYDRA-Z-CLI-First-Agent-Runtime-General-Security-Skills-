from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Callable, Optional, List
import importlib
import pkgutil

@dataclass
class SkillSpec:
    name: str
    description: str
    risk: str  # low/medium/high
    run: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
    # run(args, ctx) -> dict

def load_skills() -> Dict[str, SkillSpec]:
    # Loads built-in skills under hydra_z.skills.*
    from hydra_z import skills as skills_pkg

    registry: Dict[str, SkillSpec] = {}
    for m in pkgutil.iter_modules(skills_pkg.__path__, skills_pkg.__name__ + "."):
        mod = importlib.import_module(m.name)
        spec = getattr(mod, "SKILL", None)
        if spec and isinstance(spec, SkillSpec):
            registry[spec.name] = spec
    return registry
