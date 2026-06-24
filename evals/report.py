from __future__ import annotations
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from .models import EvalReport, TieredResult, LLMReview, Severity

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


# ── Tiered report ─────────────────────────────────────────────────────────────

_TIER_LABELS = {
    1: "Spec Compliance",
    2: "Security",
    3: "Token Efficiency",
    4: "Effectiveness",
}

_GRADE_COLOR = {
    "excellent": "green",
    "good": "cyan",
    "needs work": "yellow",
    "poor": "red",
}


def print_tiered_report(result: TieredResult, llm_review: LLMReview | None = None) -> None:
    grade_color = _GRADE_COLOR.get(result.grade, "white")

    header = Text()
    header.append(result.skill_name, style="bold white")
    header.append(f"  score {result.score:.0f}/100  ", style="dim")
    header.append(result.grade.upper(), style=f"bold {grade_color}")
    console.print(Panel(header, title="Tiered Eval", border_style=grade_color))

    # Per-tier summary
    by_tier: dict[int, list] = {1: [], 2: [], 3: [], 4: []}
    for f in result.findings:
        by_tier[f.tier].append(f)

    summary = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    summary.add_column("Tier", width=30)
    summary.add_column("Status")
    for tier_num, label in _TIER_LABELS.items():
        tier_findings = by_tier[tier_num]
        errors = sum(1 for f in tier_findings if f.severity == Severity.ERROR)
        warnings = sum(1 for f in tier_findings if f.severity == Severity.WARNING)
        if errors:
            status = f"[red]✗ {errors} error{'s' if errors > 1 else ''}"
            if warnings:
                status += f", {warnings} warning{'s' if warnings > 1 else ''}"
            status += "[/red]"
        elif warnings:
            status = f"[yellow]⚠ {warnings} warning{'s' if warnings > 1 else ''}[/yellow]"
        else:
            status = "[green]✓ pass[/green]"
        summary.add_row(f"[dim]Tier {tier_num}[/dim] — {label}", status)
    console.print(summary)

    # Detailed findings
    if result.findings:
        fp_codes = {x["code"] for x in (llm_review.false_positives if llm_review else [])}
        for f in result.findings:
            is_fp = f.code in fp_codes
            sev_style = "red" if f.severity == Severity.ERROR else "yellow"
            fp_tag = " [dim](likely false positive)[/dim]" if is_fp else ""
            console.print(f"  [{sev_style}]{f.code} {f.severity.value.upper()}[/{sev_style}]  {f.message}{fp_tag}")

    # LLM review extras
    if llm_review and llm_review.additional_observations:
        console.print("\n[dim]LLM observations:[/dim]")
        for obs in llm_review.additional_observations:
            sev = obs.get("severity", "info")
            color = {"error": "red", "warning": "yellow"}.get(sev, "dim")
            console.print(f"  [{color}]{obs.get('message', '')}[/{color}]")

    console.print()
