"""Tier 1 — Spec compliance."""
import pytest
from evals.tiers import tier1_spec
from evals.models import Severity
from pathlib import Path


def _run(name="my-skill", description="Use when X.", tools=None, body="1. Do this."):
    return tier1_spec.check(Path("."), name, description, tools if tools is not None else ["Bash"], body)


def _codes(findings):
    return {f.code for f in findings}


class TestT101_Name:
    def test_missing_name_raises_error(self):
        assert "T1.01" in _codes(_run(name=""))

    def test_present_name_no_t101(self):
        assert "T1.01" not in _codes(_run(name="my-skill"))


class TestT102_Description:
    def test_missing_description_raises_error(self):
        assert "T1.02" in _codes(_run(description=""))

    def test_whitespace_only_description_raises_error(self):
        assert "T1.02" in _codes(_run(description="   "))

    def test_present_description_no_t102(self):
        assert "T1.02" not in _codes(_run(description="Use when X."))


class TestT103_Tools:
    def test_empty_tools_is_warning(self):
        assert "T1.03" in _codes(_run(tools=[]))

    def test_tools_present_no_warning(self):
        assert "T1.03" not in _codes(_run(tools=["Bash"]))


class TestT104_NameFormat:
    @pytest.mark.parametrize("name", [
        "MySkill", "my_skill", "MY-SKILL", "1myskill", "-myskill", "my skill",
    ])
    def test_invalid_kebab_names(self, name):
        assert "T1.04" in _codes(_run(name=name))

    @pytest.mark.parametrize("name", [
        "my-skill", "compose-animations", "a", "skill-v2", "android-junit5",
    ])
    def test_valid_kebab_names(self, name):
        assert "T1.04" not in _codes(_run(name=name))


class TestT105_Body:
    def test_empty_body_is_error(self):
        assert "T1.05" in _codes(_run(body=""))

    def test_whitespace_body_is_error(self):
        assert "T1.05" in _codes(_run(body="  \n\t  "))

    def test_non_empty_body_no_error(self):
        assert "T1.05" not in _codes(_run(body="1. Do something."))


class TestT106_UnknownTools:
    def test_unknown_tool_is_warning(self):
        assert "T1.06" in _codes(_run(tools=["FakeToolXYZ"]))

    def test_mcp_prefixed_tool_allowed(self):
        assert "T1.06" not in _codes(_run(tools=["mcp__my_server__my_tool"]))

    def test_known_tools_no_warning(self):
        assert "T1.06" not in _codes(_run(tools=["Bash", "Read", "Write", "Edit"]))


class TestCleanSkill:
    def test_fully_valid_skill_has_no_errors(self):
        findings = _run(
            name="my-skill",
            description="Use when doing X. Triggered by: keyword.",
            tools=["Bash", "Read"],
            body="1. Run the command.\n2. Verify the output.",
        )
        assert not any(f.severity == Severity.ERROR for f in findings)
