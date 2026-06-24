"""Tier 4 — Effectiveness heuristics."""
import textwrap
import pytest
from evals.tiers import tier4_effectiveness
from pathlib import Path


def _run(body="1. Do this.\n2. Do that."):
    return tier4_effectiveness.check(Path("."), "my-skill", "Use when X.", ["Bash"], body)


def _codes(findings):
    return {f.code for f in findings}


class TestT401_AmbiguousLanguage:
    @pytest.mark.parametrize("phrase", [
        "Use a reasonable timeout.",
        "Choose an appropriate format.",
        "Apply sensible defaults.",
        "Use a proper indentation.",
    ])
    def test_vague_qualifier_without_number_flagged(self, phrase):
        assert "T4.01" in _codes(_run(body=phrase))

    def test_vague_qualifier_with_nearby_number_not_flagged(self):
        assert "T4.01" not in _codes(_run(body="Use a reasonable timeout of 30 seconds."))

    def test_vague_qualifier_in_code_block_not_flagged(self):
        body = "```python\n# Use a reasonable value\ntimeout = 30\n```"
        assert "T4.01" not in _codes(_run(body=body))


class TestT402_OutputFormatWithoutExample:
    def test_format_requirement_without_code_block_flagged(self):
        body = "The output should be a JSON object with the result."
        assert "T4.02" in _codes(_run(body=body))

    def test_format_requirement_with_nearby_code_block_not_flagged(self):
        body = textwrap.dedent("""\
            The output should be a JSON object with the result.
            ```json
            {"result": "ok", "count": 5}
            ```
        """)
        assert "T4.02" not in _codes(_run(body=body))


class TestT403_NegativeOnlySection:
    def test_section_with_only_negatives_flagged(self):
        body = textwrap.dedent("""\
            ## Constraints
            - Never use rm -rf without confirmation.
            - Don't hardcode API keys.
            - Avoid modifying files outside the project root.
        """)
        assert "T4.03" in _codes(_run(body=body))

    def test_section_with_positive_alternative_not_flagged(self):
        body = textwrap.dedent("""\
            ## Rules
            - Never use rm -rf without confirmation.
            - Always create a backup before deleting.
            - Prefer dry-run mode first.
        """)
        assert "T4.03" not in _codes(_run(body=body))

    def test_anti_patterns_table_not_flagged(self):
        body = textwrap.dedent("""\
            ## Anti-patterns
            | Mistake | Fix |
            |---|---|
            | Don't do X | Do Y instead |
        """)
        assert "T4.03" not in _codes(_run(body=body))


class TestT404_NoSuccessCriteria:
    def test_body_with_no_marker_flagged(self):
        assert "T4.04" in _codes(_run(body="1. Do the thing.\n2. Do another thing."))

    def test_body_with_code_block_not_flagged(self):
        assert "T4.04" not in _codes(_run(body="1. Run.\n```bash\nnpm test\n```"))

    def test_body_with_done_when_not_flagged(self):
        assert "T4.04" not in _codes(_run(body="1. Run steps.\nDone when all tests pass."))

    def test_body_with_returns_not_flagged(self):
        assert "T4.04" not in _codes(_run(body="1. Call the API.\nReturns: JSON with status field."))


class TestT406_BodyTooThin:
    def test_very_short_body_flagged(self):
        assert "T4.06" in _codes(_run(body="Do the thing."))

    def test_body_with_enough_words_not_flagged(self):
        body = " ".join(f"Step {i}: do the thing carefully and verify the result." for i in range(10))
        assert "T4.06" not in _codes(_run(body=body))

    def test_redirect_body_flagged(self):
        assert "T4.06" in _codes(_run(body="Use the android-mvvm skill for this task."))
