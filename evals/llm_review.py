"""Phase 2 — LLM review of deterministic findings for false-positive filtering."""
from __future__ import annotations
import json
import re
from .models import TieredResult, LLMReview
from . import claude_client as cc

_MODEL = "claude-haiku-4-5-20251001"


def _parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def review(result: TieredResult, skill_body: str) -> LLMReview:
    """Send deterministic findings to an LLM and return a structured review."""
    if not result.findings:
        return LLMReview()

    findings_text = "\n".join(
        f"  [{f.code}] {f.severity.value.upper()}: {f.message}"
        for f in result.findings
    )

    prompt = f"""You are reviewing the output of a deterministic linter for Claude Code skill files.
The linter uses pattern-matching; it can produce false positives.

Skill body (first 2000 chars):
{skill_body[:2000]}

Linter findings:
{findings_text}

For each finding, decide: is it a genuine issue or a false positive?
Also note any issues the linter missed.

Return ONLY valid JSON with this exact schema (no prose, no code fences):
{{
  "false_positives": [
    {{"code": "<T#.##>", "reason": "<why it is not a real issue>"}}
  ],
  "confirmed": [
    {{"code": "<T#.##>", "note": "<any additional context or fix suggestion>"}}
  ],
  "additional_observations": [
    {{"severity": "error|warning|info", "message": "<observation>"}}
  ]
}}"""

    raw, _ = cc.call(prompt=prompt, model=_MODEL)
    try:
        data = _parse_json(raw)
        return LLMReview(
            false_positives=[{"code": x["code"], "reason": x.get("reason", "")} for x in data.get("false_positives", [])],
            confirmed=[{"code": x["code"], "reason": x.get("note", "")} for x in data.get("confirmed", [])],
            additional_observations=data.get("additional_observations", []),
        )
    except Exception:
        return LLMReview(
            additional_observations=[{"severity": "error", "message": "LLM review failed to parse response"}]
        )
