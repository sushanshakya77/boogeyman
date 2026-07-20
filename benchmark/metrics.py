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


def _pp(base: float, ret: float) -> str:
    d = round((ret - base) * 100)
    return f"{d:+d} pp" if d else "0"


def render_comparison(base: dict, ret: dict, meta: dict) -> str:
    classes = sorted(set(base["per_class"]) | set(ret["per_class"]))

    def rate(s, cls):
        if cls not in s["per_class"]:
            return "-"
        c, t = s["per_class"][cls]
        return f"{c}/{t} ({c / t:.0%})"

    class_rows = "\n".join(
        f"| {cls} | {rate(base, cls)} | {rate(ret, cls)} |" for cls in classes
    )
    return f"""# Benchmark results

Does retrieving similar past bugs and injecting them into the prompt improve the
review? Same {base['n']} mutants, two configs, only retrieval changes.

- **Model**: {meta['model']}
- **Retrieval**: {meta['embed']}
- **AST context**: {meta['context']}
- **Corpus**: {meta['corpus']} ({base['n']} mutants)
- **Date**: {meta['date']}

## Baseline (LLM + context) vs. Retrieval

| Metric | Baseline | + Retrieval | Delta |
|---|---|---|---|
| Recall (bugs caught) | {base['recall']:.0%} ({base['tp']}/{base['n']}) | **{ret['recall']:.0%}** ({ret['tp']}/{ret['n']}) | {_pp(base['recall'], ret['recall'])} |
| Precision | {base['precision']:.0%} | {ret['precision']:.0%} | {_pp(base['precision'], ret['precision'])} |
| F1 | {base['f1']:.2f} | {ret['f1']:.2f} | {ret['f1'] - base['f1']:+.2f} |
| False-positive rate (correct code) | {base['fpr']:.0%} | {ret['fpr']:.0%} | {_pp(base['fpr'], ret['fpr'])} |
| Mean latency / review | {base['mean_latency']:.1f}s | {ret['mean_latency']:.1f}s | {ret['mean_latency'] - base['mean_latency']:+.1f}s |

For FPR, lower is better; a positive delta there is a regression.

## Recall by bug class

| Bug class | Baseline | + Retrieval |
|---|---|---|
{class_rows}

## Notes / threats to validity

- Retrieval corpus is DISJOINT from the benchmark corpus (same bug classes,
  different code) — this measures generalization, not leakage.
- Synthetic mutants may not resemble real bugs; treat as a controlled lower bound,
  to be validated against a handful of real commits.
- Recall uses +/-1 line tolerance on the reported location.
- Small corpus ({base['n']} mutants): numbers are directional, not publication-grade.
  Expand `benchmark/corpus/` and the seed set to tighten confidence intervals.
"""
