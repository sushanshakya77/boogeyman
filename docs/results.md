# Benchmark results

Does retrieving similar past bugs and injecting them into the prompt improve the
review? Same 15 mutants, two configs, only retrieval changes.

- **Model**: qwen2.5-coder:7b
- **Retrieval**: nomic-embed-text + FAISS (top-3)
- **AST context**: on (enclosing function via stdlib ast)
- **Corpus**: benchmark/corpus (15 mutants)
- **Date**: 2026-07-21

## Baseline (LLM + context) vs. Retrieval

| Metric | Baseline | + Retrieval | Delta |
|---|---|---|---|
| Recall (bugs caught) | 40% (6/15) | **33%** (5/15) | -7 pp |
| Precision | 38% | 29% | -8 pp |
| F1 | 0.39 | 0.31 | -0.07 |
| False-positive rate (correct code) | 53% | 47% | -7 pp |
| Mean latency / review | 4.9s | 5.4s | +0.5s |

For FPR, lower is better; a positive delta there is a regression.

## Recall by bug class

| Bug class | Baseline | + Retrieval |
|---|---|---|
| comparator | 0/6 (0%) | 0/6 (0%) |
| drop_guard | 1/1 (100%) | 1/1 (100%) |
| invert_bool | 0/1 (0%) | 0/1 (0%) |
| off_by_one | 1/2 (50%) | 0/2 (0%) |
| swap_args | 4/5 (80%) | 4/5 (80%) |

## Notes / threats to validity

- Retrieval corpus is DISJOINT from the benchmark corpus (same bug classes,
  different code) — this measures generalization, not leakage.
- Synthetic mutants may not resemble real bugs; treat as a controlled lower bound,
  to be validated against a handful of real commits.
- Recall uses +/-1 line tolerance on the reported location.
- Small corpus (15 mutants): numbers are directional, not publication-grade.
  Expand `benchmark/corpus/` and the seed set to tighten confidence intervals.
