"""Tier 4 — Effectiveness heuristics: clarity, examples, success criteria, body depth."""
from __future__ import annotations
import re
from pathlib import Path
from ..models import Finding, Severity

# Vague qualifiers that should have a nearby concrete value or specific name
_AMBIGUOUS = re.compile(
    r"\b(reasonable|appropriate|sensible|suitable|adequate|sufficient|"
    r"good\s+practice|proper(?!\s+noun))\b",
    re.IGNORECASE,
)

# Output-format requirements that should be backed by a code example
_OUTPUT_FORMAT = re.compile(
    r"(output\s+(should|must)\s+be"
    r"|return\s+(?:a\s+)?(?:JSON|YAML|XML|CSV|markdown|table)\b"
    r"|format\s+the\s+output\s+as"
    r"|produce\s+a\s+report"
    r"|emit\s+(?:a\s+)?(?:JSON|structured)\b"
    r"|the\s+response\s+(?:should|must)\s+(?:include|contain|have))\b",
    re.IGNORECASE,
)

# Success / output-contract markers
_SUCCESS_MARKERS = re.compile(
    r"(output[:\s]|returns?[:\s]|result[:\s]"
    r"|success\s+(?:criteria|when|if)"
    r"|expected\s+output|done\s+when|complete\s+when"
    r"|exit\s+code|exit\s+status"
    r"|```)",  # any code block counts
    re.IGNORECASE,
)

# Negative-only list item starters (no positive alternative in same section)
_NEGATIVE_START = re.compile(
    r"^[-*]\s+(never|don'?t|do\s+not|avoid|prohibited|must\s+not)\b",
    re.IGNORECASE | re.MULTILINE,
)
_POSITIVE_ITEM = re.compile(
    r"^[-*]\s+(?!never|don'?t|do\s+not|avoid|prohibited|must\s+not)\w",
    re.IGNORECASE | re.MULTILINE,
)

# Pure-redirect body markers
_REDIRECT = re.compile(
    r"(see\s+the\s+\S+\s+skill|use\s+the\s+\S+-\S+\s+skill|delegate\s+to|refer\s+to\b)",
    re.IGNORECASE,
)


def _strip_code_blocks(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def _has_nearby_code(body: str, pos: int, window: int = 500) -> bool:
    snippet = body[max(0, pos - window): pos + window]
    return "```" in snippet


def _has_nearby_number(body: str, pos: int, window: int = 120) -> bool:
    snippet = body[max(0, pos - window): pos + window]
    return bool(re.search(r"\b\d+\b", snippet))


def _sections(body: str) -> list[str]:
    """Split body into sections at markdown headings."""
    return re.split(r"^#{1,3}\s+.+$", body, flags=re.MULTILINE)


def check(
    skill_path: Path,
    name: str,
    description: str,
    tools: list[str],
    body: str,
) -> list[Finding]:
    findings: list[Finding] = []
    prose_body = _strip_code_blocks(body)

    # T4.01 — ambiguous language without nearby concrete value
    ambiguous_hits: list[str] = []
    for m in _AMBIGUOUS.finditer(prose_body):
        if not _has_nearby_number(prose_body, m.start()):
            ambiguous_hits.append(m.group())
    if ambiguous_hits:
        sample = ", ".join(list(dict.fromkeys(ambiguous_hits))[:3])
        findings.append(Finding(tier=4, code="T4.01", severity=Severity.WARNING,
            message=f"Ambiguous qualifier(s) without a concrete value: {sample} — "
                    "replace with a specific number, name, or criterion"))

    # T4.02 — output format required but no code example nearby
    m = _OUTPUT_FORMAT.search(body)
    if m and not _has_nearby_code(body, m.start()):
        findings.append(Finding(tier=4, code="T4.02", severity=Severity.WARNING,
            message="Output format specified but no concrete example code block found nearby"))

    # T4.03 — section with only negative instructions and no positive alternative
    for section in _sections(body):
        neg_items = _NEGATIVE_START.findall(section)
        pos_items = _POSITIVE_ITEM.findall(section)
        if len(neg_items) >= 2 and not pos_items:
            findings.append(Finding(tier=4, code="T4.03", severity=Severity.WARNING,
                message="Section with only 'never/don't/avoid' items and no positive alternative — "
                        "add what to do instead"))
            break  # one report is enough

    # T4.04 — no success criteria or output contract anywhere
    if not _SUCCESS_MARKERS.search(body):
        findings.append(Finding(tier=4, code="T4.04", severity=Severity.WARNING,
            message="No success criteria or output contract — add 'done when X', "
                    "expected output, or a code example"))

    # T4.05 — scripts present but exit codes beyond 0/1 are undocumented
    scripts_dir = skill_path / "scripts"
    if scripts_dir.is_dir():
        for script in scripts_dir.rglob("*"):
            if script.suffix not in {".sh", ".py", ".rb", ".js", ".ts"}:
                continue
            content = script.read_text(errors="ignore")
            uses_exit = bool(re.search(r"\bexit\b|\bsys\.exit\b", content))
            has_non_01 = bool(re.search(r"\bexit\s+[2-9]\d*\b|sys\.exit\([2-9]", content))
            has_docs = bool(re.search(r"exit\s+(code|status)\s*[=:]?\s*\d", content, re.IGNORECASE))
            if uses_exit and not has_non_01 and not has_docs:
                findings.append(Finding(tier=4, code="T4.05", severity=Severity.WARNING,
                    message=f"{script.name}: only exit codes 0/1 used without documentation — "
                            "add a comment describing what each code signals"))

    # T4.06 — body too thin or pure redirect (capped score if fires)
    body_words = len(body.split())
    has_scripts = scripts_dir.is_dir() and any(scripts_dir.iterdir()) if (skill_path / "scripts").is_dir() else False
    is_redirect = body_words < 60 and bool(_REDIRECT.search(body))

    if is_redirect:
        findings.append(Finding(tier=4, code="T4.06", severity=Severity.ERROR,
            message="Body appears to be a pure redirect to another skill — "
                    "add substantive instructions or inline the relevant rules"))
    elif body_words < 80 and not has_scripts:
        findings.append(Finding(tier=4, code="T4.06", severity=Severity.ERROR,
            message=f"Skill body too thin ({body_words} words, no scripts/) — "
                    "add enough instructions to guide the agent"))

    return findings
