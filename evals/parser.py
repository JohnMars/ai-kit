from __future__ import annotations
from pathlib import Path
import frontmatter
import yaml
from .models import Skill, TestCase


def parse_skill(path: Path) -> Skill:
    """Accept either a skill directory (contains SKILL.md) or a direct .md file."""
    skill_file = path / "SKILL.md" if path.is_dir() else path
    post = frontmatter.load(str(skill_file))
    return Skill(
        name=post.metadata.get("name", path.name),
        description=str(post.metadata.get("description", "")).strip(),
        tools=list(post.metadata.get("tools", [])),
        body=post.content.strip(),
        path=path,
    )


def find_skill_dirs(skills_root: Path) -> list[Path]:
    """Return all skill directories (contain SKILL.md) under skills_root, at any depth."""
    return sorted(p.parent for p in skills_root.rglob("SKILL.md"))


def find_test_cases(skill_path: Path, tests_root: Path | None = None) -> list[TestCase]:
    if tests_root is None:
        tests_root = skill_path.parent.parent / "tests"
    skill_tests_dir = tests_root / skill_path.name
    if not skill_tests_dir.exists():
        return []
    cases = []
    for f in sorted(skill_tests_dir.glob("*.yaml")):
        data = yaml.safe_load(f.read_text())
        cases.append(TestCase(
            id=data.get("id", f.stem),
            prompt=data["prompt"],
            grading_criteria=data.get("grading_criteria", []),
        ))
    return cases
