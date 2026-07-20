"""Curated bug exemplars for the retrieval corpus.

DELIBERATELY DISJOINT from benchmark/corpus/ — different code, same bug classes.
This keeps the retrieval test honest: we measure "has the model seen this SHAPE of
bug before", not leakage of the exact benchmarked code. `code` is embedded and
searched; `hint` is the lesson injected into the prompt on a hit."""

SEEDS = [
    {"code": "if idx <= len(buf):\n    return buf[idx]", "bug_class": "comparator",
     "hint": "off-by-one: index goes out of range when idx == len(buf); use < not <="},
    {"code": "while low <= high:\n    mid = (low + high) / 2", "bug_class": "comparator",
     "hint": "boundary/type: integer midpoint should use // not /"},
    {"code": "for k in range(len(rows) + 1):\n    use(rows[k])", "bug_class": "off_by_one",
     "hint": "range(len(x) + 1) reads one past the end -> IndexError"},
    {"code": "for j in range(1, len(a)):\n    a[j - 1] = a[j + 1]", "bug_class": "off_by_one",
     "hint": "a[j + 1] overruns the last element"},
    {"code": "def send(user):\n    return user.email.lower()", "bug_class": "drop_guard",
     "hint": "missing None check: user or user.email may be None -> AttributeError"},
    {"code": "def frac(a, b):\n    return a / b", "bug_class": "drop_guard",
     "hint": "missing guard for b == 0 -> ZeroDivisionError"},
    {"code": "def rect(w, h):\n    return area(h, w)", "bug_class": "swap_args",
     "hint": "arguments passed in the wrong order relative to the definition"},
    {"code": "shift(dy, dx)  # def shift(dx, dy)", "bug_class": "swap_args",
     "hint": "positional args swapped: dx and dy are reversed"},
    {"code": "if is_admin or is_owner:\n    delete()", "bug_class": "invert_bool",
     "hint": "wrong connective: likely should require both (and), not either (or)"},
    {"code": "return valid and not expired or forced", "bug_class": "invert_bool",
     "hint": "operator precedence / and-or mix changes the intended condition"},
    {"code": "f = open(path)\ndata = f.read()\nreturn data", "bug_class": "resource_leak",
     "hint": "file handle never closed; use a with-statement"},
    {"code": "total = 0\nfor x in xs:\n    total = x", "bug_class": "logic",
     "hint": "assignment instead of accumulation: total = x should be total += x"},
    {"code": "if items == None:\n    return", "bug_class": "logic",
     "hint": "use 'is None', not '== None', for identity checks"},
    {"code": "n = len(s)\nreturn s[n]", "bug_class": "off_by_one",
     "hint": "s[len(s)] is out of range; last valid index is len(s) - 1"},
]
