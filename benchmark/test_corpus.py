"""The corpus is ground truth: every function in benchmark/corpus/ must be CORRECT,
or mutants of it score the reviewer against a bug that was already there.
Lives outside corpus/ so collect_mutants() never globs it.

    uv run python -m benchmark.test_corpus
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "corpus"))

import records
import samples
import stats
import text


def check_samples() -> None:
    assert samples.clamp(5, 0, 10) == 5
    assert samples.clamp(-1, 0, 10) == 0
    assert samples.clamp(99, 0, 10) == 10
    assert samples.total([1, 2, 3]) == 6
    assert samples.first_or_none([7, 8]) == 7
    assert samples.first_or_none(None) is None
    assert samples.divide(6, 3) == 2
    assert samples.ratio(6, 3) == 2
    assert samples.ascending_positive(1, 5) and not samples.ascending_positive(5, 1)
    assert not samples.ascending_positive(-1, 5)
    assert samples.average([2, 4]) == 3
    assert samples.average([]) == 0
    assert samples.contains([1, 2], 2) and not samples.contains([1, 2], 9)


def check_text() -> None:
    assert text.truncate("abc", 5) == "abc"
    assert text.truncate("abcdef", 3) == "abc..."
    assert text.split_pair("k=v", "=") == ("k", "v")
    assert text.split_pair("kv", "=") is None
    assert text.starts_with_any("foobar", ["baz", "foo"])
    assert not text.starts_with_any("foobar", ["baz"])
    assert text.is_blank(None) and text.is_blank("  ") and not text.is_blank("x")
    assert text.strip_suffix("file.py", ".py") == "file"
    assert text.strip_suffix("file.py", ".md") == "file.py"
    assert text.strip_suffix("file.py", "") == "file.py"
    assert text.indent_of("    x") == 4
    assert text.join_nonempty(["a", " ", "b"], "-") == "a-b"
    assert text.head_lines("1\n2\n3", 2) == "1\n2"
    assert text.head_lines("1\n2", 5) == "1\n2"


def check_stats() -> None:
    assert stats.safe_div(6, 3) == 2
    assert stats.safe_div(6, 0) == 0
    assert stats.pct_change(100, 150) == 0.5
    assert stats.pct_change(0, 5) == 0.0
    assert stats.in_range(5, 1, 10) and not stats.in_range(0, 1, 10)
    assert stats.in_range(1, 1, 10) and stats.in_range(10, 1, 10)
    assert stats.count_above([1, 5, 9], 4) == 2
    assert stats.running_max([3, 9, 4]) == 9
    assert stats.running_max([]) is None
    assert stats.normalize([0, 5, 10]) == [0.0, 0.5, 1.0]
    assert stats.normalize([2, 2]) == [0.0, 0.0]
    assert stats.percentile([3, 1, 2], 0.5) == 2
    assert stats.percentile([], 0.5) is None
    assert stats.all_within([1, 2], 5) and not stats.all_within([1, 9], 5)
    assert stats.trimmed([5, 1, 3, 2, 4], 1) == [2, 3, 4]
    assert stats.trimmed([1, 2], 1) == []


def check_records() -> None:
    assert records.get_field({"a": 1}, "a") == 1
    assert records.get_field(None, "a") is None
    assert records.merge_prefer({"a": 1}, {"a": 2, "b": 3}) == {"a": 2, "b": 3}
    assert records.pick({"a": 1, "b": 2}, ["a", "z"]) == {"a": 1}
    assert records.is_active({"enabled": True, "banned": False})
    assert not records.is_active({"enabled": True, "banned": True})
    admin, owner = {"role": "admin", "id": 1}, {"role": "user", "id": 2}
    assert records.has_access(admin, {"owner_id": 99})
    assert records.has_access(owner, {"owner_id": 2})
    assert not records.has_access(owner, {"owner_id": 3})
    assert records.newest([{"t": 1}, {"t": 5}], "t") == {"t": 5}
    assert records.group_sizes([{"k": "a"}, {"k": "a"}, {"k": "b"}], "k") == {"a": 2, "b": 1}
    assert records.drop_missing([{"f": 1}, {"f": None}, {}], "f") == [{"f": 1}]
    assert records.page([1, 2, 3, 4, 5], 2, 1) == [3, 4]
    assert records.page([1, 2], 2, 5) == []


if __name__ == "__main__":
    for fn in (check_samples, check_text, check_stats, check_records):
        fn()
    print("ok: corpus is correct")
