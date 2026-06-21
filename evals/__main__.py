from __future__ import annotations
from pathlib import Path
from typing import Optional

import typer

from .models import EvalReport
from .parser import parse_skill, find_test_cases
from .static_eval import evaluate_static
from .dynamic_eval import evaluate_dynamic
from .report import print_report, console

app = typer.Typer(
    name="eval-skill",
    help="Evaluate Claude Code skills for token efficiency and instruction quality.",
    no_args_is_help=True,
)


@app.command()
def main(
    path: Path = typer.Argument(..., help="Skill .md file or directory of skills"),
    dynamic: bool = typer.Option(False, "--dynamic", "-d", help="Run dynamic eval against test cases"),
    tests_dir: Optional[Path] = typer.Option(None, "--tests", "-t", help="Root directory for test cases (default: ./tests)"),
) -> None:
    skill_paths = sorted(path.glob("*.md")) if path.is_dir() else [path]
    if not skill_paths:
        console.print(f"[red]No .md skill files found at {path}[/red]")
        raise typer.Exit(1)

    for skill_path in skill_paths:
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


if __name__ == "__main__":
    app()
