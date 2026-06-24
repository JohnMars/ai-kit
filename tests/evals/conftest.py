"""Auto-loaded pytest helpers for tier tests. No relative imports needed."""
from __future__ import annotations
from pathlib import Path
import pytest


def run_tier(module, *, name="my-skill", description="Use when doing X. Triggered by: keyword-a.", tools=None, body="1. Do this.\n2. Do that.", skill_path=None):
    return module.check(
        skill_path or Path("."),
        name,
        description,
        tools if tools is not None else ["Bash"],
        body,
    )


def codes(findings) -> set[str]:
    return {f.code for f in findings}
