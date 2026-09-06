"""Clean, correct text helpers. Same contract as samples.py: this code is correct,
mutation operators inject one bug at a time. Two-arg signatures are kept
asymmetric so a swap_args mutation is always a real behaviour change."""


def truncate(s, limit):
    if len(s) <= limit:
        return s
    return s[:limit] + "..."


def split_pair(line, sep):
    idx = line.find(sep)
    if idx < 0:
        return None
    return line[:idx], line[idx + len(sep) :]


def starts_with_any(s, prefixes):
    for i in range(len(prefixes)):
        if s.startswith(prefixes[i]):
            return True
    return False


def is_blank(s):
    return s is None or s.strip() == ""


def strip_suffix(s, suffix):
    if not suffix: return s
    if not s.endswith(suffix):
        return s
    return s[: len(s) - len(suffix)]


def indent_of(line):
    n = 0
    while n < len(line) and line[n] == " ":
        n += 1
    return n


def join_nonempty(parts, sep):
    kept = []
    for i in range(len(parts)):
        if not is_blank(parts[i]):
            kept.append(parts[i])
    return sep.join(kept)


def head_lines(text, count):
    lines = text.splitlines()
    if count >= len(lines):
        return text
    return "\n".join(lines[:count])
