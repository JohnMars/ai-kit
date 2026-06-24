"""Tier 1 — Spec compliance: frontmatter fields, name format, non-empty body."""
from __future__ import annotations
import re
from pathlib import Path
from ..models import Finding, Severity

# Tools listed in Claude Code docs / shipped in the default tool set.
# MCP tools can't be enumerated, so unknowns are warnings, not errors.
KNOWN_TOOLS = {
    "Bash", "Read", "Write", "Edit", "Glob", "Grep",
    "WebFetch", "WebSearch", "Agent", "NotebookEdit",
    "Skill", "ToolSearch", "ScheduleWakeup",
    "AskUserQuestion", "EnterPlanMode", "ExitPlanMode",
    "TaskCreate", "TaskUpdate", "TaskGet", "TaskList",
}

_KEBAB = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def check(
    skill_path: Path,
    name: str,
    description: str,
    tools: list[str],
    body: str,
) -> list[Finding]:
    findings: list[Finding] = []

    if not name:
        findings.append(Finding(tier=1, code="T1.01", severity=Severity.ERROR,
            message="Missing 'name' field in frontmatter"))
    elif not _KEBAB.match(name):
        findings.append(Finding(tier=1, code="T1.04", severity=Severity.ERROR,
            message=f"'name' must be kebab-case (lowercase, hyphens only), got: {name!r}"))

    if not description.strip():
        findings.append(Finding(tier=1, code="T1.02", severity=Severity.ERROR,
            message="Missing 'description' field in frontmatter"))

    if not tools:
        findings.append(Finding(tier=1, code="T1.03", severity=Severity.WARNING,
            message="No 'tools' declared in frontmatter — skill will have no tool access"))

    unknown = [t for t in tools if t not in KNOWN_TOOLS and not t.startswith("mcp__")]
    for t in unknown:
        findings.append(Finding(tier=1, code="T1.06", severity=Severity.WARNING,
            message=f"Unrecognised tool {t!r} — verify it is available in the target Claude Code version"))

    if not body.strip():
        findings.append(Finding(tier=1, code="T1.05", severity=Severity.ERROR,
            message="Skill body is empty"))

    return findings
