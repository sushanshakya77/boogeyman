# Boogeyman — bugs' worst nightmare

A local, `$0`, on-device code-review assistant. It reads a git diff, reasons about
the changed code with a local code LLM, and reports structured findings (issue,
severity, location, explanation, suggested fix).

The project also tests one hypothesis honestly: **does retrieving similar past
bug-fixes and injecting them into the prompt improve the review over the LLM
reasoning alone?** The answer is measured, not assumed — a mutation-based
benchmark writes results to `docs/results.md`.

## Stack

- Ollama + `qwen2.5-coder:7b` (Q4) — local inference on an Apple M4 / 16 GB
- Stdlib `ast` — enclosing-function + imports context around each diff hunk (Tree-sitter deferred to multi-language)
- `nomic-embed-text` + FAISS — retrieval over a corpus of past bug-fixes
- Mutation-based benchmark — perfect ground truth, no hand-labeling

## Usage

```bash
uv sync
ollama serve            # if not already running
ollama pull qwen2.5-coder:7b
uv run boogeyman <path-to-git-repo>       # reviews the working-tree diff
uv run boogeyman <path> --staged          # reviews staged changes
```
