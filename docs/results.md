# Benchmark results

Does retrieving similar past bugs and injecting them into the prompt improve the
review? Same 70 mutants, two configs, only retrieval changes.

- **Model**: qwen2.5-coder:7b
- **Retrieval**: nomic-embed-text + FAISS (top-3)
- **AST context**: on (enclosing function via stdlib ast)
- **Corpus**: benchmark/corpus (70 mutants)
- **Date**: 2026-07-29

## Baseline (LLM + context) vs. Retrieval

| Metric | Baseline | + Retrieval | Delta |
|---|---|---|---|
| Recall (bugs caught) | 27% (19/70) | **27%** (19/70) | 0 |
| Precision | 31% | 22% | -9 pp |
| F1 | 0.29 | 0.24 | -0.05 |
| False-positive rate (correct code) | 37% | 56% | +19 pp |
| Mean latency / review | 3.9s | 5.4s | +1.5s |

For FPR, lower is better; a positive delta there is a regression.

## Recall by bug class

| Bug class | Baseline | + Retrieval |
|---|---|---|
| comparator | 1/25 (4%) | 2/25 (8%) |
| drop_guard | 4/6 (67%) | 4/6 (67%) |
| invert_bool | 0/5 (0%) | 0/5 (0%) |
| off_by_one | 1/10 (10%) | 3/10 (30%) |
| swap_args | 13/24 (54%) | 10/24 (42%) |

## Notes / threats to validity

- Retrieval corpus is DISJOINT from the benchmark corpus (same bug classes,
  different code) — this measures generalization, not leakage.
- Synthetic mutants may not resemble real bugs; treat as a controlled lower bound,
  to be validated against a handful of real commits.
- Recall uses +/-1 line tolerance on the reported location.
- Small corpus (70 mutants): numbers are directional, not publication-grade.
  Expand `benchmark/corpus/` and the seed set to tighten confidence intervals.
