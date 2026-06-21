# ai-kit

A personal toolkit for AI-driven development — reusable skills, tools, and evaluation infrastructure for Claude Code agents.

## What's here

| Directory | Purpose |
|---|---|
| `skills/` | Reusable Claude Code skill definitions (one directory per skill) |
| `tests/` | Test cases for each skill (`tests/<skill-name>/*.yaml`) |
| `evals/` | Skill evaluation and installation framework |

## Installing skills

Skills are symlinked into `~/.claude/skills/` so they stay live with the repo — no re-install after edits.

```bash
uv sync

# Install all skills
python -m evals install

# Install a single skill
python -m evals install evaluate-skill
```

## Evaluating skills

Scores each skill on **token efficiency** (context cost) and **instruction quality** (routing specificity + actionable fraction).

```bash
# Static eval — token count + routing/quality assessment (fast, no test cases needed)
python -m evals eval skills/my-skill/

# Static + dynamic — also runs skill against test cases and grades output
python -m evals eval skills/my-skill/ --dynamic

# Eval all skills
python -m evals eval skills/ --dynamic
```

### Scoring

| Metric | What it measures |
|---|---|
| `description_tokens` | Tokens in the routing description (target: <50) |
| `body_tokens` | Tokens injected per invocation (flag: >2000) |
| `routing_quality` | 0–1: how specifically the description triggers the skill |
| `actionable_fraction` | 0–1: direct instructions vs. filler in the body |
| `overall_score` | 35% static + 65% dynamic (static-only when no test cases) |

Uses your Claude Code subscription — no API key required.

## Adding a skill

1. Create `skills/<name>/SKILL.md`:

```markdown
---
name: my-skill
description: >
  Use this skill when the user asks to <specific trigger condition>.
tools:
  - Bash
  - Read
---

1. Step one.
2. Step two.
```

2. Add test cases in `tests/<name>/01_basic.yaml`:

```yaml
id: 01_basic
prompt: "User message that should trigger the skill"
grading_criteria:
  - "Response must do X"
  - "Response must not do Y"
```

3. Run the evaluator and iterate until score is green, then install.
