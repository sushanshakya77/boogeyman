import ast
import re
from pathlib import Path

# ponytail: stdlib `ast` covers Python-only AST context with zero deps.
# Swap in tree-sitter here when a second language (TS/JS) is added.


def changed_lines(diff_text: str) -> dict[str, set[int]]:
    """Map each file in the diff to the set of new-file line numbers it added."""
    files: dict[str, set[int]] = {}
    cur: str | None = None
    newno = 0
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            path = line[4:].strip()
            path = path[2:] if path.startswith("b/") else path
            cur = None if path == "/dev/null" else path
            if cur:
                files.setdefault(cur, set())
        elif line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            newno = int(m.group(1)) if m else 0
        elif cur is not None:
            if line.startswith("+") and not line.startswith("+++"):
                files[cur].add(newno)
                newno += 1
            elif line.startswith("-") and not line.startswith("---"):
                pass  # removed line: does not advance the new-file counter
            elif line.startswith(" "):
                newno += 1
    return files


def _enclosing_blocks(src: str, lines: set[int]) -> list[str]:
    """Smallest def/class in `src` covering each changed line, deduped, in order."""
    tree = ast.parse(src)
    srclines = src.splitlines()
    spans = [
        (node.lineno, node.end_lineno, node.name)
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and node.end_lineno is not None
    ]
    chosen: dict[tuple[int, int], None] = {}
    for L in lines:
        best: tuple[int, int, str] | None = None
        for s, e, _ in spans:
            if s <= L <= e and (best is None or (e - s) < (best[1] - best[0])):
                best = (s, e, _)
        if best:
            chosen[(best[0], best[1])] = None
    return ["\n".join(srclines[s - 1 : e]) for s, e in sorted(chosen)]


def _imports(src: str) -> list[str]:
    tree = ast.parse(src)
    srclines = src.splitlines()
    out = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            out.append("\n".join(srclines[node.lineno - 1 : node.end_lineno]))
    return out


def _section(relpath: str, lines: set[int], src: str) -> str | None:
    try:
        blocks = _enclosing_blocks(src, lines)
        imports = _imports(src)
    except SyntaxError:
        return None  # mid-edit / unparsable source: fall back to diff only
    if not blocks and not imports:
        return None
    parts = [f"### {relpath} (language: python)"]
    if imports:
        parts.append("Imports:\n" + "\n".join(imports))
    if blocks:
        parts.append("Enclosing function(s)/class(es):\n\n" + "\n\n".join(blocks))
    return "\n".join(parts)


def build_context_from_sources(diff_text: str, sources: dict[str, str]) -> str:
    """Same as build_context but reads file contents from a dict, not disk."""
    sections = []
    for relpath, lines in changed_lines(diff_text).items():
        if not relpath.endswith(".py") or relpath not in sources:
            continue
        section = _section(relpath, lines, sources[relpath])
        if section:
            sections.append(section)
    return "\n\n".join(sections)


def build_context(repo: str, diff_text: str) -> str:
    """Return enclosing-function + imports context for Python files in the diff."""
    sources = {}
    for relpath in changed_lines(diff_text):
        f = Path(repo) / relpath
        if f.exists():
            sources[relpath] = f.read_text()
    return build_context_from_sources(diff_text, sources)


if __name__ == "__main__":  # self-check: parser logic is the risky part
    diff = (
        "--- a/x.py\n+++ b/x.py\n"
        "@@ -1,3 +1,4 @@\n def f():\n     a = 1\n+    b = 2\n     return a\n"
    )
    assert changed_lines(diff) == {"x.py": {3}}, changed_lines(diff)
    src = "import os\n\ndef f():\n    a = 1\n    b = 2\n    return a\n"
    assert _enclosing_blocks(src, {5}) == ["def f():\n    a = 1\n    b = 2\n    return a"]
    assert _imports(src) == ["import os"]
    print("ok")
