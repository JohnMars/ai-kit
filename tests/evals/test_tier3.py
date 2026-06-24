"""Tier 3 — Token efficiency checks."""
import pytest
from evals.tiers import tier3_tokens
from pathlib import Path


def _run(description="Use when X. Triggered by: keyword.", body="1. Do this.", name="my-skill"):
    return tier3_tokens.check(Path("."), name, description, ["Bash"], body)


def _codes(findings):
    return {f.code for f in findings}


class TestT301_HardTokenCap:
    def test_over_hard_cap_is_error(self):
        # Build a description clearly over the 256-token hard cap
        long_desc = ("Use when implementing " + "complex architectural patterns " * 30
                     + "Triggered by: " + "keyword-" + ", keyword-".join(str(i) for i in range(50)))
        assert "T3.01" in _codes(_run(description=long_desc))

    def test_under_hard_cap_no_error(self):
        assert "T3.01" not in _codes(_run(description="Use when X. Triggered by: keyword-a, keyword-b."))


class TestT302_SoftTokenCap:
    def test_over_soft_cap_is_warning(self):
        # ~140 tokens: over soft cap (124) but under hard cap (256)
        mid_desc = ("Use when implementing Jetpack Compose animations. "
                    "Triggered by: " + ", ".join(f"compose-keyword-{i}" for i in range(20)))
        findings = _run(description=mid_desc)
        assert "T3.01" in _codes(findings) or "T3.02" in _codes(findings)

    def test_under_soft_cap_no_warning(self):
        findings = _run(description="Use when X. Triggered by: foo, bar.")
        assert "T3.02" not in _codes(findings)
        assert "T3.01" not in _codes(findings)


class TestT303_LargeCodeBlock:
    def _block(self, lines: int, lang: str = "bash") -> str:
        inner = "\n".join(f"echo line {i}" for i in range(lines))
        return f"```{lang}\n{inner}\n```"

    def test_block_over_limit_flagged(self):
        body = self._block(tier3_tokens.MAX_INLINE_CODE_LINES + 1)
        assert "T3.03" in _codes(_run(body=body))

    def test_block_at_limit_not_flagged(self):
        body = self._block(tier3_tokens.MAX_INLINE_CODE_LINES)
        assert "T3.03" not in _codes(_run(body=body))

    def test_short_block_not_flagged(self):
        assert "T3.03" not in _codes(_run(body="```bash\necho hello\n```"))


class TestT304_LargeTable:
    def _table(self, rows: int) -> str:
        return "| A | B |\n|---|---|\n" + "".join(f"| r{i} | v{i} |\n" for i in range(rows))

    def test_table_over_limit_flagged(self):
        assert "T3.04" in _codes(_run(body=self._table(tier3_tokens.MAX_TABLE_ROWS + 1)))

    def test_table_at_limit_not_flagged(self):
        assert "T3.04" not in _codes(_run(body=self._table(tier3_tokens.MAX_TABLE_ROWS)))


class TestT305_VerboseProse:
    def test_long_paragraph_flagged(self):
        long_para = " ".join(f"word{i}" for i in range(tier3_tokens.MAX_PROSE_WORDS + 5))
        assert "T3.05" in _codes(_run(body=long_para))

    def test_short_paragraph_not_flagged(self):
        assert "T3.05" not in _codes(_run(body="This skill helps you do the thing correctly."))

    def test_prose_in_code_block_not_flagged(self):
        long = " ".join(f"# word{i}" for i in range(200))
        assert "T3.05" not in _codes(_run(body=f"```bash\n{long}\n```"))


class TestT306_StandardToolUsage:
    @pytest.mark.parametrize("phrase", [
        "Use the Bash tool to run commands",
        "Use the Read tool to read the file",
        "Use the Edit tool to modify source",
    ])
    def test_standard_explanation_flagged(self, phrase):
        assert "T3.06" in _codes(_run(body=phrase))

    def test_implicit_tool_use_not_flagged(self):
        assert "T3.06" not in _codes(_run(body="1. Read the SKILL.md file.\n2. Run the tests."))


class TestT307_UnconditionalPreload:
    @pytest.mark.parametrize("phrase", [
        "Always read reference/config.md first",
        "At the start, read reference/data.yaml",
    ])
    def test_unconditional_preload_flagged(self, phrase):
        assert "T3.07" in _codes(_run(body=phrase))

    def test_conditional_preload_not_flagged(self):
        body = "If the user asks about configuration, read reference/config.md."
        assert "T3.07" not in _codes(_run(body=body))
