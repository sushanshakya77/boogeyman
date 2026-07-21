# Boogeyman: bugs' worst nightmare

I was staring at a diff I'd already read three times, still not sure whether the
thing I'd just changed was fine, and wondered if I could get a model to do that
pass for me. Not a cloud one. Something on my laptop, free, offline, that I could
run on every diff without thinking about it. So I built Boogeyman.

It reads a git diff, reasons about the changed code with a local code LLM, and
reports structured findings (issue, severity, location, explanation, suggested fix).

The project also tests one hypothesis honestly: **does retrieving similar past
bug-fixes and injecting them into the prompt improve the review over the LLM
reasoning alone?** The answer is measured, not assumed. A mutation-based
benchmark writes results to `docs/results.md`.

**Headline result:** on this benchmark, retrieval **hurt**: recall 40%→33%,
precision 38%→29%. The model also stayed blind to boundary-comparator bugs (0/6)
and false-flagged correct code about half the time. A negative result, reported straight.
Full method, findings, and next steps in **[`docs/writeup.md`](docs/writeup.md)**.

## Stack

- Ollama + `qwen2.5-coder:7b` (Q4), local inference on an Apple M4 / 16 GB
- Stdlib `ast` for enclosing-function + imports context around each diff hunk (Tree-sitter deferred to multi-language)
- `nomic-embed-text` + FAISS for retrieval over a corpus of past bug-fixes
- Mutation-based benchmark, so the ground truth is exact and nothing needs hand-labeling

## On the model

Everything runs on `qwen2.5-coder:7b` at Q4 through Ollama, on an M4 with 16 GB.
I picked it because it's the smallest thing I tried that actually reasons about
code instead of pattern-matching it, and it still leaves enough memory to keep
working while it runs. The 3B version was too weak to be worth benchmarking.

I'm not attached to it. If a different local model does better on the same
mutants, I'll swap it in. The benchmark exists so that's a measurement and not a
guess.

## Usage

```bash
uv sync
ollama serve            # if not already running
ollama pull qwen2.5-coder:7b
uv run boogeyman <path-to-git-repo>       # reviews the working-tree diff
uv run boogeyman <path> --staged          # reviews staged changes
```
