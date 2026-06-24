"""Tier 2 — Security: destructive operations, hardcoded user paths."""
from __future__ import annotations
import re
from pathlib import Path
from ..models import Finding, Severity

# (regex, human label) pairs for destructive shell/SQL/git operations
_DESTRUCTIVE: list[tuple[str, str]] = [
    (r"\brm\s+-[rRf]*f[rRf]*\b",             "rm -rf"),
    (r"\brm\s+-r\b",                           "rm -r"),
    (r"\bgit\s+push\s+(-f|--force)\b",        "git push --force"),
    (r"\bgit\s+reset\s+--hard\b",             "git reset --hard"),
    (r"\bgit\s+clean\s+(-f|--force)\b",       "git clean -f"),
    (r"\bDROP\s+(TABLE|DATABASE|SCHEMA)\b",   "DROP TABLE/DATABASE"),
    (r"\bTRUNCATE\s+TABLE\b",                 "TRUNCATE TABLE"),
    (r"\bDELETE\s+FROM\b",                    "DELETE FROM"),
    (r"\bmkfs\b",                             "mkfs"),
    (r"\bdd\s+if=",                           "dd if="),
]

_SAFEGUARDS = re.compile(
    r"\b(confirm\w*|backup|warning|caution|dry.run|check\s+first|verif\w+|"
    r"undo|revert|safeguard|protect|recover\w*|restore|snapshot)\b",
    re.IGNORECASE,
)

# User-specific path patterns — flag paths that embed an actual username
_USER_PATHS = re.compile(
    r"(?:"
    r"/Users/(?!zhanibekmarshal\b|\$|\{)[A-Za-z][A-Za-z0-9_.-]+/"  # macOS
    r"|/home/(?!\$|\{)[A-Za-z][A-Za-z0-9_.-]+/"                    # Linux
    r"|C:\\\\Users\\\\[A-Za-z][A-Za-z0-9_. -]+\\\\"                # Windows
    r")"
)


def _nearby(text: str, pos: int, window: int = 300) -> str:
    return text[max(0, pos - window): pos + window]


def check(
    skill_path: Path,
    name: str,
    description: str,
    tools: list[str],
    body: str,
) -> list[Finding]:
    findings: list[Finding] = []
    full = description + "\n" + body

    # T2.01 — hardcoded user paths
    for m in _USER_PATHS.finditer(full):
        findings.append(Finding(tier=2, code="T2.01", severity=Severity.ERROR,
            message=f"Hardcoded user path {m.group()!r} — use ~ or $HOME/$USER instead"))

    # T2.02 — destructive operations without a nearby safeguard
    seen_labels: set[str] = set()
    for pattern, label in _DESTRUCTIVE:
        for m in re.finditer(pattern, full, re.IGNORECASE):
            if label in seen_labels:
                break
            context = _nearby(full, m.start())
            if not _SAFEGUARDS.search(context):
                findings.append(Finding(tier=2, code="T2.02", severity=Severity.WARNING,
                    message=f"Destructive operation '{label}' without a nearby safeguard "
                            "(confirm / backup / dry-run / warning)"))
                seen_labels.add(label)

    return findings
