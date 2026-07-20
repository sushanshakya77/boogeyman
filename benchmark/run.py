"""Run the mutation benchmark and write docs/results.md.

Runs every mutant through two configs on the SAME inputs:
  baseline  = LLM + AST context
  retrieval = baseline + top-k similar past bugs injected
so the only variable is retrieval, and the delta is attributable to it.

    uv run python -m benchmark.run
"""

import difflib
import time
from datetime import date
from pathlib import Path

from boogeyman.context import build_context_from_sources
from boogeyman.llm import review_diff
from boogeyman.retrieval.index import Retriever, added_code
from benchmark.metrics import Trial, aggregate, render_comparison
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


def _review(diff: str, source: str, path: str, retriever: Retriever | None):
    ctx = build_context_from_sources(diff, {path: source})
    examples = retriever.block(added_code(diff)) if retriever else ""
    t0 = time.time()
    findings = review_diff(diff, ctx, examples).findings
    return findings, time.time() - t0


def run_trial(m: Mutant, retriever: Retriever | None) -> Trial:
    buggy_diff = make_diff(m.path, m.clean, m.mutated)
    buggy, buggy_lat = _review(buggy_diff, m.mutated, m.path, retriever)
    caught = any(abs(f.line - m.line) <= 1 for f in buggy)
    off_target = sum(1 for f in buggy if abs(f.line - m.line) > 1)

    fix_diff = make_diff(m.path, m.mutated, m.clean)
    fix, fix_lat = _review(fix_diff, m.clean, m.path, retriever)

    return Trial(m.bug_class, caught, off_target, len(fix), buggy_lat, fix_lat)


def _pass(label: str, mutants: list[Mutant], retriever: Retriever | None) -> list[Trial]:
    trials = []
    for i, m in enumerate(mutants, 1):
        t = run_trial(m, retriever)
        print(
            f"[{label} {i}/{len(mutants)}] {m.bug_class:11} L{m.line:<3} "
            f"caught={int(t.caught)} off={t.off_target} fix_fp={int(t.fix_findings > 0)} "
            f"({t.buggy_latency:.1f}s)",
            flush=True,
        )
        trials.append(t)
    return trials


def main() -> None:
    mutants = collect_mutants()
    base = aggregate(_pass("base", mutants, None))
    print("building retriever...", flush=True)
    retriever = Retriever()
    ret = aggregate(_pass("retr", mutants, retriever))

    meta = {
        "model": "qwen2.5-coder:7b",
        "embed": "nomic-embed-text + FAISS (top-3)",
        "context": "on (enclosing function via stdlib ast)",
        "corpus": "benchmark/corpus",
        "date": str(date.today()),
    }
    RESULTS.write_text(render_comparison(base, ret, meta))
    print(f"\nwrote {RESULTS}")
    for name, s in (("baseline", base), ("retrieval", ret)):
        print(f"{name:10} recall={s['recall']:.0%} precision={s['precision']:.0%} "
              f"f1={s['f1']:.2f} fpr={s['fpr']:.0%}")


if __name__ == "__main__":
    main()
