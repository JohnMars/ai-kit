---
name: evaluate-skill
description: >
  Use this skill when asked to evaluate, score, test, or check the quality
  of a skill in this repository. Triggered by: "evaluate skill", "score this
  skill", "check skill quality", "run the evaluator on".
tools:
  - Bash
  - Read
---

1. Identify the target skill:
   - If the user named a skill, resolve it to `skills/<name>/`.
   - If the user pointed at the current file, use that path.
   - If no skill is specified, list `skills/` and ask the user to pick one.

2. Check whether test cases exist:
   ```bash
   ls tests/<skill-name>/
   ```

3. Run the static eval first (always):
   ```bash
   python -m evals skills/<name>/
   ```

4. If test cases exist, or if the user explicitly asks for dynamic eval, also run:
   ```bash
   python -m evals skills/<name>/ --dynamic
   ```

5. Read the output and report:
   - State the overall score and what drove it (routing quality, actionable fraction, test pass rate).
   - List every issue flagged under "Issues".
   - Give one concrete recommendation to improve the lowest-scoring dimension.

6. If the user says "fix it" or "improve it", apply the smallest change to the skill file that addresses the top issue, then re-run the evaluator to confirm the score improved.
