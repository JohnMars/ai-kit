# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
uv sync   # install dependencies — no API key needed, uses Claude Code subscription auth
```

## Commands

```bash
# Static eval only (no API calls beyond token counting + quality assessment)
python -m evals skills/my-skill.md

# Static + dynamic eval (runs skill against test cases via Claude API)
python -m evals skills/my-skill.md --dynamic

# Eval all skills in the directory
python -m evals skills/ --dynamic

# Custom test cases directory
python -m evals skills/my-skill.md --dynamic --tests /path/to/tests
```

## Architecture

```
ai-kit/
├── skills/          # Skill definitions (.md with YAML frontmatter)
├── tests/           # Test cases per skill (tests/<skill-name>/*.yaml)
└── evals/           # Evaluation framework (Python package)
    ├── claude_client.py  # Wrapper around `claude -p` subprocess (subscription auth)
    ├── models.py         # Pydantic models: Skill, TestCase, StaticResult, DynamicResult, EvalReport
    ├── parser.py         # Parse skill .md files and test .yaml files
    ├── static_eval.py    # Phase 1: token counting + LLM quality assessment
    ├── dynamic_eval.py   # Phase 2: run skill against test cases + LLM judge
    ├── report.py         # Rich terminal report
    └── __main__.py       # Typer CLI entry point
```

## Skill format

Skills are `.md` files with YAML frontmatter:

```markdown
---
name: skill-name
description: >
  One or two sentences naming the exact trigger conditions.
  Used for routing — must be specific enough to avoid false positives.
tools:
  - Bash
  - Read
---

Numbered, imperative instructions only. No background prose.
```

## Test case format

Test cases live at `tests/<skill-name>/<n>_<label>.yaml`:

```yaml
id: 01_basic
prompt: "The user message that should exercise this skill"
grading_criteria:
  - "What the response must do or contain to pass"
```

A test passes when the LLM judge scores it ≥ 0.7.

## Evaluation methodology

**Phase 1 — Static (cheap, always runs)**
- `description_tokens`: tokens in the routing description (target <50)
- `body_tokens`: tokens injected per invocation (flag if >2000)
- `routing_quality`: 0–1, LLM-judged specificity of the trigger description
- `actionable_fraction`: 0–1, fraction of body that is direct instruction vs. filler

**Phase 2 — Dynamic (requires `--dynamic` flag)**
- Skill body is injected as a system prompt; Claude runs against each test case
- An LLM judge scores the response 0–1 against the grading criteria
- `overall_score` = 35% static + 65% dynamic when dynamic results exist

**Auth:** All LLM calls go through `claude -p` subprocess using your Claude Code subscription (OAuth). No `ANTHROPIC_API_KEY` required. Token counting uses `tiktoken` (`cl100k_base`) locally — no API call needed.

Models used:
- Static quality assessment + LLM judge: `claude-haiku-4-5-20251001` (fast)
- Dynamic runner: `claude-sonnet-4-6`
