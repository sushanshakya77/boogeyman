"""Mutation operators: inject exactly one bug into clean source.

Each operator yields a mutant (one single-line change) with the 1-based line it
broke and a bug_class. Operators are token-aware (via `tokenize`) so they never
mutate inside strings or comments — a mutation there would be a bogus "bug" that
unfairly counts as a miss. One-line diffs keep ground truth unambiguous."""

import ast
import io
import re
import tokenize
from dataclasses import dataclass

COMPARATOR_FLIP = {"<": "<=", "<=": "<", ">": ">=", ">=": ">", "==": "!=", "!=": "=="}
BOOL_FLIP = {"and": "or", "or": "and"}


@dataclass
class Mutant:
    path: str
    clean: str
    mutated: str
    line: int
    bug_class: str


def _tokens(src: str) -> list[tokenize.TokenInfo]:
    return list(tokenize.generate_tokens(io.StringIO(src).readline))


def _string_lines(toks: list[tokenize.TokenInfo]) -> set[int]:
    """1-based line numbers covered by a string or comment token."""
    out: set[int] = set()
    for t in toks:
        if t.type in (tokenize.STRING, tokenize.COMMENT, tokenize.FSTRING_MIDDLE):
            out.update(range(t.start[0], t.end[0] + 1))
    return out


def _splice(src: str, row: int, scol: int, ecol: int, new: str) -> str:
    lines = src.splitlines(keepends=True)
    line = lines[row - 1]
    lines[row - 1] = line[:scol] + new + line[ecol:]
    return "".join(lines)


def _sites(clean: str):
    """Yield (line_1based, mutated_source_or_None, bug_class). None = delete line."""
    toks = _tokens(clean)
    str_lines = _string_lines(toks)
    lines = clean.splitlines()

    # token-precise: comparators and boolean connectives (safe inside strings)
    for t in toks:
        if t.start[0] != t.end[0]:
            continue
        if t.type == tokenize.OP and t.string in COMPARATOR_FLIP:
            yield t.start[0], _splice(clean, t.start[0], t.start[1], t.end[1], COMPARATOR_FLIP[t.string]), "comparator"
        elif t.type == tokenize.NAME and t.string in BOOL_FLIP:
            yield t.start[0], _splice(clean, t.start[0], t.start[1], t.end[1], BOOL_FLIP[t.string]), "invert_bool"

    # line-regex operators, skipping any line inside a string/comment
    for i, line in enumerate(lines):
        if (i + 1) in str_lines:
            continue
        if re.search(r"range\(len\(\w+\)\)", line):
            new = re.sub(r"range\(len\((\w+)\)\)", r"range(len(\1) + 1)", line, count=1)
            yield i + 1, "\n".join(lines[:i] + [new] + lines[i + 1 :]) + "\n", "off_by_one"
        m = re.search(r"\b(\w+)\((\w+), (\w+)\)", line)
        if m:
            new = line[: m.start()] + f"{m.group(1)}({m.group(3)}, {m.group(2)})" + line[m.end() :]
            yield i + 1, "\n".join(lines[:i] + [new] + lines[i + 1 :]) + "\n", "swap_args"
        if re.match(r"\s*if .+:\s*return", line):
            yield i + 1, None, "drop_guard"


def mutants_for(path: str, clean: str) -> list[Mutant]:
    out = []
    lines = clean.splitlines()
    for line1, mutated, bug_class in _sites(clean):
        if mutated is None:  # drop_guard: delete the guard line
            mutated = "\n".join(lines[: line1 - 1] + lines[line1:]) + "\n"
        if mutated == clean:
            continue
        try:
            ast.parse(mutated)  # only keep mutants that still compile
        except SyntaxError:
            continue
        out.append(Mutant(path, clean, mutated, line1, bug_class))
    return out


if __name__ == "__main__":  # self-check: string content is never mutated
    src = (
        '"""a docstring with and / or and < inside it"""\n'
        "def f(x, lo):\n"
        "    if x < lo:\n"
        "        return lo\n"
        "    if lo is None: return 0\n"
        "    return both(x, lo)\n"
    )
    ms = mutants_for("f.py", src)
    classes = {m.bug_class for m in ms}
    assert {"comparator", "swap_args", "drop_guard"} <= classes, classes
    assert all(m.line != 1 for m in ms), "docstring (line 1) must never be mutated"
    for m in ms:
        assert m.mutated != m.clean
        ast.parse(m.mutated)
    print(f"ok: {len(ms)} mutants, classes={sorted(classes)}, none touched the docstring")
