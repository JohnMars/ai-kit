# ai-kit

A personal toolkit for AI-driven development — reusable skills, tools, and evaluation infrastructure for Claude Code agents.

## What's here

| Directory | Purpose |
|---|---|
| `skills/` | Reusable Claude Code skill definitions (`.md` with YAML frontmatter) |
| `tests/` | Test cases for each skill (`tests/<skill-name>/*.yaml`) |
| `evals/` | Skill evaluation framework — static analysis + dynamic LLM testing |

## Skill evaluator

Evaluates skills on two dimensions: **token efficiency** (how much context they consume) and **instruction quality** (how actionable and well-routed they are).

```bash
uv sync

# Static eval — token count + routing/quality assessment
python -m evals skills/my-skill.md

# Static + dynamic — also runs skill against test cases and grades output
python -m evals skills/my-skill.md --dynamic

# Eval all skills
python -m evals skills/ --dynamic
```

Uses your Claude Code subscription — no API key required.

### Scoring

| Metric | What it measures |
|---|---|
| `description_tokens` | Tokens in the routing description (target: <50) |
| `body_tokens` | Tokens injected per invocation (flag: >2000) |
| `routing_quality` | 0–1: how specifically the description triggers the skill |
| `actionable_fraction` | 0–1: direct instructions vs. filler in the body |
| `overall_score` | 35% static + 65% dynamic (static-only if no test cases) |

## Adding a skill

1. Create `skills/<name>.md`:

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

3. Run the evaluator and iterate until score is green.
