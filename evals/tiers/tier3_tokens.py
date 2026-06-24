"""Tier 3 — Token efficiency: routing budget, inline code/table size, prose density."""
from __future__ import annotations
import re
from pathlib import Path
from ..models import Finding, Severity
from .. import claude_client as cc

SOFT_TOKEN_CAP = 124
HARD_TOKEN_CAP = 256
MAX_INLINE_CODE_LINES = 40      # longer blocks belong in scripts/
MAX_TABLE_ROWS = 20             # bigger tables belong in reference/
MAX_PROSE_WORDS = 100           # prose paragraphs above this are usually trimmable

_STANDARD_TOOL_USAGE = re.compile(
    r"use\s+the\s+(Bash|Read|Write|Edit|Grep|Glob)\s+tool\s+to\s+\w+"
    r"|the\s+(Bash|Read|Write|Edit)\s+tool\s+(runs|reads|writes|modifies)\b",
    re.IGNORECASE,
)

_UNCONDITIONAL_PRELOAD = re.compile(
    r"(always|first|at\s+the\s+start|unconditionally).{0,80}read.{0,60}reference/",
    re.IGNORECASE | re.DOTALL,
)


def _iter_code_blocks(body: str):
    """Yield (fence_lang, line_count) for each code block."""
    in_block = False
    lang = ""
    count = 0
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_block:
                yield lang, count
                in_block = False
                count = 0
            else:
                in_block = True
                lang = stripped[3:].strip()
        elif in_block:
            count += 1
    if in_block and count:
        yield lang, count


def _table_row_counts(body: str) -> list[int]:
    """Return data-row count (excluding header + separator) per markdown table."""
    counts: list[int] = []
    in_table = False
    rows = 0
    for line in body.splitlines():
        s = line.strip()
        is_row = s.startswith("|") and s.endswith("|")
        is_sep = is_row and re.fullmatch(r"[\|\-: ]+", s)
        if is_row and not is_sep:
            if not in_table:
                in_table = True
                rows = 0  # header row — don't count
            else:
                rows += 1
        elif is_sep:
            pass  # separator — skip
        else:
            if in_table:
                counts.append(rows)
            in_table = False
            rows = 0
    if in_table:
        counts.append(rows)
    return counts


def _prose_word_counts(body: str) -> list[int]:
    """Return word count per prose paragraph (skips code blocks, headers, tables, lists)."""
    in_code = False
    counts: list[int] = []
    current: list[str] = []

    def flush():
        if current:
            counts.append(len(" ".join(current).split()))
            current.clear()

    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            flush()
            continue
        if in_code:
            continue
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("#") or s.startswith("|") or re.match(r"^(\d+\.|[-*+])\s", s):
            flush()
        else:
            current.append(line)

    flush()
    return counts


def check(
    skill_path: Path,
    name: str,
    description: str,
    tools: list[str],
    body: str,
) -> list[Finding]:
    findings: list[Finding] = []

    # T3.01 / T3.02 — routing token budget
    routing_tokens = cc.count_tokens(name + " " + description)
    if routing_tokens > HARD_TOKEN_CAP:
        findings.append(Finding(tier=3, code="T3.01", severity=Severity.ERROR,
            message=f"Name + description = {routing_tokens} tokens "
                    f"(hard cap {HARD_TOKEN_CAP}) — bloats routing context on every turn"))
    elif routing_tokens > SOFT_TOKEN_CAP:
        findings.append(Finding(tier=3, code="T3.02", severity=Severity.WARNING,
            message=f"Name + description = {routing_tokens} tokens (soft cap {SOFT_TOKEN_CAP})"))

    # T3.03 — large inline code blocks
    for lang, n_lines in _iter_code_blocks(body):
        if n_lines > MAX_INLINE_CODE_LINES:
            findings.append(Finding(tier=3, code="T3.03", severity=Severity.WARNING,
                message=f"Inline code block ({lang or 'no lang'}) has {n_lines} lines "
                        f"(>{MAX_INLINE_CODE_LINES}) — move executable code to scripts/"))

    # T3.04 — large inline tables
    for row_count in _table_row_counts(body):
        if row_count > MAX_TABLE_ROWS:
            findings.append(Finding(tier=3, code="T3.04", severity=Severity.WARNING,
                message=f"Inline table has {row_count} data rows "
                        f"(>{MAX_TABLE_ROWS}) — move reference data to reference/"))

    # T3.05 — verbose prose paragraphs
    for wc in _prose_word_counts(body):
        if wc > MAX_PROSE_WORDS:
            findings.append(Finding(tier=3, code="T3.05", severity=Severity.WARNING,
                message=f"Prose paragraph has {wc} words "
                        f"(>{MAX_PROSE_WORDS}) — trim or convert to numbered rules"))

    # T3.06 — explains standard tool mechanics the agent already knows
    if _STANDARD_TOOL_USAGE.search(body):
        findings.append(Finding(tier=3, code="T3.06", severity=Severity.WARNING,
            message="Explains standard tool usage the agent already knows — remove to save tokens"))

    # T3.07 — unconditionally instructs preloading a reference file
    if _UNCONDITIONAL_PRELOAD.search(body):
        findings.append(Finding(tier=3, code="T3.07", severity=Severity.WARNING,
            message="Unconditional 'always read reference/...' — preload only when needed"))

    return findings
