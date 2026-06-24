from __future__ import annotations
import json
import re
from . import claude_client as cc
from .models import Skill, StaticResult


def _parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)

_JUDGE = "claude-haiku-4-5-20251001"


def _assess_routing(description: str) -> tuple[float, list[str]]:
    if not description.strip():
        return 0.0, ["Missing routing description — skill will never be triggered correctly"]

    result, _ = cc.call(
        prompt=f"""Rate this skill routing description for specificity and uniqueness.
A good description: names concrete trigger conditions, is unique enough to avoid false positives, is concise.

Description:
{description}

Return JSON: {{"score": <0.0-1.0>, "issues": ["<issue>", ...]}}""",
        system="You evaluate LLM agent skill routing descriptions. Return JSON only, no prose.",
        model=_JUDGE,
    )
    try:
        data = _parse_json(result)
        return float(data["score"]), data.get("issues", [])
    except Exception:
        return 0.5, []


def _assess_body(body: str) -> tuple[float, list[str]]:
    if not body.strip():
        return 0.0, ["Empty skill body"]

    result, _ = cc.call(
        prompt=f"""Analyze this skill body.
ACTIONABLE = direct rules, numbered steps, constraints, imperatives ("do X", "never Y").
NON-ACTIONABLE = background context, verbose examples, redundant explanations, disclaimers.

Body (first 3000 chars):
{body[:3000]}

Return JSON: {{"actionable_fraction": <0.0-1.0>, "issues": ["<issue>", ...]}}""",
        system="You evaluate LLM agent skill bodies. Return JSON only, no prose.",
        model=_JUDGE,
    )
    try:
        data = _parse_json(result)
        return float(data["actionable_fraction"]), data.get("issues", [])
    except Exception:
        return 0.5, []


def evaluate_static(skill: Skill) -> StaticResult:
    desc_tokens = cc.count_tokens(skill.description)
    body_tokens = cc.count_tokens(skill.body)
    routing_score, routing_issues = _assess_routing(skill.description)
    actionable_frac, body_issues = _assess_body(skill.body)

    issues = routing_issues + body_issues
    if desc_tokens > 100:
        issues.append(f"Description is verbose ({desc_tokens} tokens) — aim for <50")
    if body_tokens > 2000:
        issues.append(f"Body is large ({body_tokens} tokens) — consider progressive disclosure")
    if actionable_frac < 0.6:
        issues.append(f"Only {actionable_frac:.0%} of body is actionable — trim filler content")

    return StaticResult(
        description_tokens=desc_tokens,
        body_tokens=body_tokens,
        actionable_fraction=actionable_frac,
        routing_quality=routing_score,
        issues=issues,
    )
