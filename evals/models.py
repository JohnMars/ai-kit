from __future__ import annotations
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field


class Skill(BaseModel):
    name: str
    description: str
    tools: list[str] = Field(default_factory=list)
    body: str
    path: Path


class TestCase(BaseModel):
    id: str
    prompt: str
    grading_criteria: list[str]


class StaticResult(BaseModel):
    description_tokens: int
    body_tokens: int
    actionable_fraction: float  # 0.0–1.0: fraction of body that is direct instruction vs. filler
    routing_quality: float      # 0.0–1.0: LLM-judged specificity of the routing description
    issues: list[str] = Field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        return self.description_tokens + self.body_tokens


class DynamicResult(BaseModel):
    test_id: str
    score: float  # 0.0–1.0
    passed: bool  # score >= 0.7
    feedback: str
    tokens_used: int


# ── Tiered deterministic evaluator ──────────────────────────────────────────

class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class Finding(BaseModel):
    tier: int
    code: str        # e.g. "T1.01"
    severity: Severity
    message: str


class TieredResult(BaseModel):
    skill_name: str
    findings: list[Finding] = Field(default_factory=list)
    score: float     # 0–100
    grade: str       # "excellent" | "good" | "needs work" | "poor"

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == Severity.WARNING]


# ── LLM review (Phase 2) ─────────────────────────────────────────────────────

class ReviewFinding(BaseModel):
    code: str
    reason: str


class LLMReview(BaseModel):
    false_positives: list[ReviewFinding] = Field(default_factory=list)
    confirmed: list[ReviewFinding] = Field(default_factory=list)
    additional_observations: list[dict] = Field(default_factory=list)


# ── LLM-based eval (legacy) ───────────────────────────────────────────────────

class EvalReport(BaseModel):
    skill: Skill
    static: StaticResult
    dynamic: list[DynamicResult] = Field(default_factory=list)

    @property
    def overall_score(self) -> float:
        # Static contributes routing quality + actionable fraction, weighted
        static_score = (self.static.routing_quality * 0.5 + self.static.actionable_fraction * 0.5)
        if not self.dynamic:
            return static_score
        dynamic_score = sum(r.score for r in self.dynamic) / len(self.dynamic)
        return static_score * 0.35 + dynamic_score * 0.65
