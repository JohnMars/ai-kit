from __future__ import annotations
import os
from pathlib import Path
from typing import Optional

import typer

from .models import EvalReport
from .parser import parse_skill, find_skill_dirs, find_test_cases
from .static_eval import evaluate_static
from .dynamic_eval import evaluate_dynamic
from .report import print_report, console

app = typer.Typer(
    name="eval-skill",
    help="Evaluate and install Claude Code skills.",
    no_args_is_help=True,
)


def _resolve_skill_paths(path: Path) -> list[Path]:
    """Given a skill directory, skills root, or .md file — return skill paths to evaluate."""
    if path.is_dir() and (path / "SKILL.md").exists():
        return [path]
    if path.is_dir():
        return find_skill_dirs(path)
    if path.suffix == ".md" and path.exists():
        return [path]
    console.print(f"[red]No skills found at {path}[/red]")
    raise typer.Exit(1)


@app.command()
def eval(
    path: Path = typer.Argument(..., help="Skill directory, skills root, or SKILL.md file"),
    dynamic: bool = typer.Option(False, "--dynamic", "-d", help="Run dynamic eval against test cases"),
    tests_dir: Optional[Path] = typer.Option(None, "--tests", "-t", help="Root directory for test cases (default: ./tests)"),
) -> None:
    """Evaluate one or all skills for token efficiency and instruction quality."""
    for skill_path in _resolve_skill_paths(path):
        skill = parse_skill(skill_path)
        static_result = evaluate_static(skill)

        dynamic_results = []
        if dynamic:
            cases = find_test_cases(skill_path, tests_dir)
            if cases:
                dynamic_results = evaluate_dynamic(skill, cases)
            else:
                console.print(f"[dim]No test cases found for {skill_path.name} — skipping dynamic eval[/dim]")

        report = EvalReport(skill=skill, static=static_result, dynamic=dynamic_results)
        print_report(report)


@app.command()
def install(
    skill_name: Optional[str] = typer.Argument(None, help="Skill name to install (default: all)"),
    skills_root: Path = typer.Option(Path("skills"), "--skills-dir", help="Source skills directory"),
    target: Path = typer.Option(Path.home() / ".claude/skills", "--target", help="Target Claude Code skills directory"),
    copy: bool = typer.Option(False, "--copy", help="Copy files instead of symlinking"),
) -> None:
    """Install skills from this repo into ~/.claude/skills/ (symlinks by default)."""
    import shutil

    if skill_name:
        candidates = [skills_root / skill_name]
    else:
        candidates = find_skill_dirs(skills_root)

    if not candidates:
        console.print(f"[red]No skills found in {skills_root}[/red]")
        raise typer.Exit(1)

    target.mkdir(parents=True, exist_ok=True)

    for src in candidates:
        if not src.exists() or not (src / "SKILL.md").exists():
            console.print(f"[red]  ✗ {src.name}: not found or missing SKILL.md[/red]")
            continue

        dst = target / src.name

        if dst.is_symlink():
            dst.unlink()
            action = "updated"
        elif dst.exists():
            console.print(f"[yellow]  ⚠ {src.name}: {dst} exists and is not a symlink — skipping (remove manually to replace)[/yellow]")
            continue
        else:
            action = "installed"

        if copy:
            shutil.copytree(src, dst)
            console.print(f"[green]  ✓ {src.name}: copied to {dst}[/green]")
        else:
            dst.symlink_to(src.resolve())
            console.print(f"[green]  ✓ {src.name}: {action} → {dst} -> {src.resolve()}[/green]")


if __name__ == "__main__":
    app()
