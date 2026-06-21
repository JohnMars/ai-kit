from __future__ import annotations
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from .models import EvalReport

console = Console()


def _color(score: float) -> str:
    if score >= 0.8:
        return "green"
    if score >= 0.5:
        return "yellow"
    return "red"


def _bar(score: float, width: int = 10) -> str:
    filled = round(score * width)
    return "█" * filled + "░" * (width - filled)


def print_report(report: EvalReport) -> None:
    s = report.static
    overall = report.overall_score

    header = Text()
    header.append(report.skill.name, style="bold white")
    header.append(f"  {report.skill.path}", style="dim")
    console.print(Panel(header, title="Skill Eval", border_style="blue"))

    # Static analysis
    static_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    static_table.add_column("", style="dim", width=22)
    static_table.add_column("")

    static_table.add_row("description tokens", str(s.description_tokens))
    static_table.add_row("body tokens", str(s.body_tokens))
    static_table.add_row("total tokens", f"[bold]{s.total_tokens}[/bold]")
    static_table.add_row(
        "routing quality",
        f"[{_color(s.routing_quality)}]{_bar(s.routing_quality)} {s.routing_quality:.0%}[/{_color(s.routing_quality)}]",
    )
    static_table.add_row(
        "actionable fraction",
        f"[{_color(s.actionable_fraction)}]{_bar(s.actionable_fraction)} {s.actionable_fraction:.0%}[/{_color(s.actionable_fraction)}]",
    )
    console.print(Panel(static_table, title="Static Analysis", border_style="dim"))

    # Issues
    if s.issues:
        console.print("[yellow]Issues:[/yellow]")
        for issue in s.issues:
            console.print(f"  [yellow]•[/yellow] {issue}")

    # Dynamic results
    if report.dynamic:
        dyn_table = Table(box=box.SIMPLE, show_header=True)
        dyn_table.add_column("Test", style="dim")
        dyn_table.add_column("Score", width=14)
        dyn_table.add_column("Tokens", justify="right")
        dyn_table.add_column("Feedback")

        for r in report.dynamic:
            c = _color(r.score)
            status = "[green]✓[/green]" if r.passed else "[red]✗[/red]"
            dyn_table.add_row(
                f"{status} {r.test_id}",
                f"[{c}]{_bar(r.score)} {r.score:.0%}[/{c}]",
                str(r.tokens_used),
                r.feedback,
            )
        console.print(Panel(dyn_table, title="Dynamic Eval", border_style="dim"))

    # Overall
    c = _color(overall)
    console.print(
        Panel(
            f"[{c}]{_bar(overall, 20)} {overall:.0%}[/{c}]",
            title="Overall Score",
            border_style=c,
        )
    )
    console.print()
