"""Orchestrates all four tiers and computes the final score."""
from __future__ import annotations
from pathlib import Path
from .models import Finding, Severity, TieredResult
from .parser import parse_skill
from .tiers import ALL_TIERS


def _compute_score(findings: list[Finding]) -> float:
    score = 100.0
    for f in findings:
        score -= 5 if f.severity == Severity.ERROR else 2

    # Hard caps
    if any(f.code in {"T1.01", "T1.02"} for f in findings):
        score = min(score, 75.0)
    if any(f.code == "T4.06" for f in findings):
        score = min(score, 35.0)

    return max(0.0, score)


def _grade(score: float) -> str:
    if score > 90:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 50:
        return "needs work"
    return "poor"


def evaluate_tiered(skill_path: Path) -> TieredResult:
    skill = parse_skill(skill_path)
    findings: list[Finding] = []
    for tier in ALL_TIERS:
        findings.extend(tier.check(skill_path, skill.name, skill.description, skill.tools, skill.body))
    score = _compute_score(findings)
    return TieredResult(skill_name=skill.name, findings=findings, score=score, grade=_grade(score))
