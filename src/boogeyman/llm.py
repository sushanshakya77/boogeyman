import ollama

from boogeyman.models import Review

MODEL = "qwen2.5-coder:7b"

SYSTEM = """You are a precise code reviewer. You are given a git diff, and often
the surrounding function/class and imports for context.

Report ONLY real, concrete bugs introduced by the added ('+') lines of the diff:
logic errors, off-by-one, null/None dereferences, wrong operators,
swapped arguments, resource leaks, missing error handling on real paths.

The surrounding-context code is for your reasoning only. Do NOT report bugs in
context lines that the diff did not change.
Do NOT report style, naming, formatting, or speculative issues.
If the diff has no real bug, return an empty findings list.
For each finding, cite the file and the line number from the diff hunk."""


def review_diff(diff_text: str, context: str = "") -> Review:
    if not diff_text.strip():
        return Review(findings=[])
    user = f"Review this diff:\n\n{diff_text}"
    if context.strip():
        user += f"\n\n## Surrounding code context (reference only)\n\n{context}"
    resp = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        format=Review.model_json_schema(),
        options={"temperature": 0},
    )
    return Review.model_validate_json(resp.message.content)
