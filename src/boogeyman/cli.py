import typer

from boogeyman.context import build_context
from boogeyman.diff import get_diff
from boogeyman.llm import review_diff

app = typer.Typer(add_completion=False, help="Boogeyman: bugs' worst nightmare — local LLM code review")


@app.command()
def review(
    repo: str = typer.Argument(".", help="Path to the git repo to review"),
    staged: bool = typer.Option(False, "--staged", help="Review staged changes instead of working tree"),
) -> None:
    diff = get_diff(repo, staged=staged)
    context = build_context(repo, diff)
    result = review_diff(diff, context)
    if not result.findings:
        typer.echo("No issues found.")
        raise typer.Exit()
    for i, f in enumerate(result.findings, 1):
        typer.echo(f"\nIssue #{i}")
        typer.echo(f"Severity: {f.severity.value}")
        typer.echo(f"Location: {f.file}:{f.line}")
        typer.echo(f"Category: {f.category}")
        typer.echo(f"Explanation:\n  {f.explanation}")
        typer.echo(f"Suggested Fix:\n  {f.suggested_fix}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
