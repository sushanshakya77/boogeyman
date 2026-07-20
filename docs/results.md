# Benchmark results

- **Model**: qwen2.5-coder:7b
- **Retrieval**: off (baseline)
- **AST context**: on (enclosing function via stdlib ast)
- **Corpus**: benchmark/corpus (15 mutants)
- **Date**: 2026-07-20

## Headline (LLM-only baseline)

| Metric | Value |
|---|---|
| Recall (bugs caught) | **40%** (6/15) |
| Precision | 38% |
| F1 | 0.39 |
| False-positive rate on correct code | 53% |
| Mean latency / review | 4.9s |

## Recall by bug class

| Bug class | Caught | Rate |
|---|---|---|
| comparator | 0/6 | 0% |
| drop_guard | 1/1 | 100% |
| invert_bool | 0/1 | 0% |
| off_by_one | 1/2 | 50% |
| swap_args | 4/5 | 80% |

## Notes / threats to validity

- Synthetic mutants may not resemble real bugs; treat this as a controlled lower
  bound, validated separately against a handful of real commits.
- Recall uses +/-1 line tolerance on the reported location.
- Small corpus (15 mutants): numbers are directional, not publication-grade.
  Expand `benchmark/corpus/` to tighten confidence intervals.
