"""Scoring for the mutation benchmark.

Definitions (stated so the numbers are defensible):
- Each mutant is one injected bug on a known line. We run TWO reviews per mutant:
    buggy review = diff (clean -> mutant); the reviewer SHOULD flag the mutated line.
    fix review   = diff (mutant -> clean); a correct change; the reviewer SHOULD stay silent.
- TP  = buggy reviews that flagged the mutated line (+/-1).       -> recall numerator
- FN  = buggy reviews that missed it.
- FP  = off-target findings on buggy reviews + any finding on fix reviews (correct code).
- recall    = TP / (TP + FN)
- precision = TP / (TP + FP)
- FPR       = fraction of fix (correct-code) reviews that produced >= 1 finding."""

from dataclasses import dataclass


@dataclass
class Trial:
    bug_class: str
    caught: bool
    off_target: int
    fix_findings: int
    buggy_latency: float
    fix_latency: float


def aggregate(trials: list[Trial]) -> dict:
    n = len(trials)
    tp = sum(t.caught for t in trials)
    fn = n - tp
    fp = sum(t.off_target for t in trials) + sum(t.fix_findings for t in trials)
    fp_reviews = sum(1 for t in trials if t.fix_findings > 0)
    lat = [t.buggy_latency for t in trials] + [t.fix_latency for t in trials]

    recall = tp / n if n else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    per_class: dict[str, list[int]] = {}
    for t in trials:
        c = per_class.setdefault(t.bug_class, [0, 0])
        c[1] += 1
        c[0] += 1 if t.caught else 0

    return {
        "n": n, "tp": tp, "fn": fn, "fp": fp,
        "recall": recall, "precision": precision, "f1": f1,
        "fpr": fp_reviews / n if n else 0.0,
        "mean_latency": sum(lat) / len(lat) if lat else 0.0,
        "per_class": per_class,
    }


def render_markdown(s: dict, meta: dict) -> str:
    rows = "\n".join(
        f"| {cls} | {caught}/{total} | {caught / total:.0%} |"
        for cls, (caught, total) in sorted(s["per_class"].items())
    )
    return f"""# Benchmark results

- **Model**: {meta['model']}
- **Retrieval**: {meta['retrieval']}
- **AST context**: {meta['context']}
- **Corpus**: {meta['corpus']} ({s['n']} mutants)
- **Date**: {meta['date']}

## Headline (LLM-only baseline)

| Metric | Value |
|---|---|
| Recall (bugs caught) | **{s['recall']:.0%}** ({s['tp']}/{s['n']}) |
| Precision | {s['precision']:.0%} |
| F1 | {s['f1']:.2f} |
| False-positive rate on correct code | {s['fpr']:.0%} |
| Mean latency / review | {s['mean_latency']:.1f}s |

## Recall by bug class

| Bug class | Caught | Rate |
|---|---|---|
{rows}

## Notes / threats to validity

- Synthetic mutants may not resemble real bugs; treat this as a controlled lower
  bound, validated separately against a handful of real commits.
- Recall uses +/-1 line tolerance on the reported location.
- Small corpus ({s['n']} mutants): numbers are directional, not publication-grade.
  Expand `benchmark/corpus/` to tighten confidence intervals.
"""
