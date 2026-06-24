"""Tier 2 — Security checks."""
import pytest
from evals.tiers import tier2_security
from pathlib import Path


def _run(body="1. Do this.", description="Use when X."):
    return tier2_security.check(Path("."), "my-skill", description, ["Bash"], body)


def _codes(findings):
    return {f.code for f in findings}


class TestT201_HardcodedPaths:
    @pytest.mark.parametrize("path_str", [
        "/Users/john/projects/",
        "/home/alice/work/",
    ])
    def test_hardcoded_user_paths_flagged(self, path_str):
        assert "T2.01" in _codes(_run(body=f"Run the script at {path_str}script.sh"))

    def test_tilde_path_not_flagged(self):
        assert "T2.01" not in _codes(_run(body="Copy files to ~/projects/"))

    def test_env_var_path_not_flagged(self):
        assert "T2.01" not in _codes(_run(body="See $HOME/config or $USER/data"))

    def test_claude_settings_path_not_flagged(self):
        assert "T2.01" not in _codes(_run(body="Skills live in ~/.claude/skills/"))


class TestT202_DestructiveOps:
    @pytest.mark.parametrize("cmd", [
        "rm -rf /tmp/cache",
        "git push --force origin main",
        "git push -f",
        "git reset --hard HEAD~1",
        "DROP TABLE users",
    ])
    def test_destructive_without_safeguard_flagged(self, cmd):
        assert "T2.02" in _codes(_run(body=f"Run: `{cmd}`"))

    def test_destructive_with_confirm_not_flagged(self):
        body = "After confirming with the user, run: `rm -rf ./dist`"
        assert "T2.02" not in _codes(_run(body=body))

    def test_destructive_with_backup_not_flagged(self):
        body = "Ensure a backup exists, then: `git reset --hard HEAD`"
        assert "T2.02" not in _codes(_run(body=body))

    def test_destructive_with_dry_run_not_flagged(self):
        body = "Use dry-run first: `git push --force --dry-run`"
        assert "T2.02" not in _codes(_run(body=body))

    def test_safe_commands_not_flagged(self):
        body = "1. Run `git status`.\n2. Run `git log --oneline`."
        assert "T2.02" not in _codes(_run(body=body))
