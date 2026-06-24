from __future__ import annotations
import json
import re
from . import claude_client as cc
from .models import Skill, TestCase, DynamicResult


def _parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)

_RUNNER = "claude-sonnet-4-6"
_JUDGE = "claude-haiku-4-5-20251001"
_PASS_THRESHOLD = 0.7


def _run(skill: Skill, prompt: str) -> tuple[str, int]:
    system = f"""You are a helpful AI assistant.

<skill name="{skill.name}">
{skill.body}
</skill>

Use the skill above when it applies to the user's request."""
    return cc.call(prompt=prompt, system=system, model=_RUNNER)


def _grade(prompt: str, response: str, criteria: list[str]) -> tuple[float, str]:
    criteria_text = "\n".join(f"- {c}" for c in criteria)
    result, _ = cc.call(
        prompt=f"""Grade this agent response.

User prompt: {prompt}

Agent response:
{response[:2000]}

Grading criteria:
{criteria_text}

Return JSON: {{"score": <0.0-1.0>, "feedback": "<one sentence>"}}""",
        system="You are a strict evaluator. Return JSON only, no prose.",
        model=_JUDGE,
    )
    try:
        data = _parse_json(result)
        return float(data["score"]), str(data["feedback"])
    except Exception:
        return 0.0, "Failed to parse grader response"


def evaluate_dynamic(skill: Skill, test_cases: list[TestCase]) -> list[DynamicResult]:
    results = []
    for case in test_cases:
        response, tokens_used = _run(skill, case.prompt)
        score, feedback = _grade(case.prompt, response, case.grading_criteria)
        results.append(DynamicResult(
            test_id=case.id,
            score=score,
            passed=score >= _PASS_THRESHOLD,
            feedback=feedback,
            tokens_used=tokens_used,
        ))
    return results
