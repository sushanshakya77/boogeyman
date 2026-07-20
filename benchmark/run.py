"""Run the mutation benchmark and write docs/results.md.

    uv run python -m benchmark.run
"""

import difflib
import time
from datetime import date
from pathlib import Path

from boogeyman.context import build_context_from_sources
from boogeyman.llm import review_diff
from benchmark.metrics import Trial, aggregate, render_markdown
from benchmark.mutate import Mutant, mutants_for

CORPUS = Path(__file__).parent / "corpus"
RESULTS = Path(__file__).parent.parent / "docs" / "results.md"


def make_diff(path: str, a: str, b: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            a.splitlines(), b.splitlines(),
            fromfile=f"a/{path}", tofile=f"b/{path}", lineterm="",
        )
    )


def collect_mutants() -> list[Mutant]:
    out = []
    for f in sorted(CORPUS.glob("*.py")):
        out += mutants_for(f.name, f.read_text())
    return out


def run_trial(m: Mutant) -> Trial:
    buggy_diff = make_diff(m.path, m.clean, m.mutated)
    ctx = build_context_from_sources(buggy_diff, {m.path: m.mutated})
    t0 = time.time()
    buggy = review_diff(buggy_diff, ctx).findings
    buggy_lat = time.time() - t0
    caught = any(abs(f.line - m.line) <= 1 for f in buggy)
    off_target = sum(1 for f in buggy if abs(f.line - m.line) > 1)

    fix_diff = make_diff(m.path, m.mutated, m.clean)
    ctx2 = build_context_from_sources(fix_diff, {m.path: m.clean})
    t0 = time.time()
    fix = review_diff(fix_diff, ctx2).findings
    fix_lat = time.time() - t0

    return Trial(m.bug_class, caught, off_target, len(fix), buggy_lat, fix_lat)


def main() -> None:
    mutants = collect_mutants()
    trials = []
    for i, m in enumerate(mutants, 1):
        t = run_trial(m)
        print(
            f"[{i}/{len(mutants)}] {m.bug_class:11} L{m.line:<3} "
            f"caught={int(t.caught)} off={t.off_target} fix_fp={int(t.fix_findings > 0)} "
            f"({t.buggy_latency:.1f}s)",
            flush=True,
        )
        trials.append(t)

    summary = aggregate(trials)
    meta = {
        "model": "qwen2.5-coder:7b",
        "retrieval": "off (baseline)",
        "context": "on (enclosing function via stdlib ast)",
        "corpus": "benchmark/corpus",
        "date": str(date.today()),
    }
    RESULTS.write_text(render_markdown(summary, meta))
    print(
        f"\nwrote {RESULTS}\n"
        f"recall={summary['recall']:.0%}  precision={summary['precision']:.0%}  "
        f"f1={summary['f1']:.2f}  fpr={summary['fpr']:.0%}  "
        f"mean_latency={summary['mean_latency']:.1f}s"
    )


if __name__ == "__main__":
    main()
