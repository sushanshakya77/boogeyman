"""FAISS nearest-neighbor over embedded bug exemplars.

Cosine similarity = inner product on L2-normalized vectors (IndexFlatIP). Flat
(brute-force) is exact and plenty for this corpus size; swap to an ANN index
(IVF/HNSW) only if the corpus grows to many thousands."""

import faiss
import numpy as np

from boogeyman.retrieval.corpus import all_examples
from boogeyman.retrieval.embed import embed


def added_code(diff_text: str) -> str:
    """The added ('+') lines of a diff — what we search the corpus with."""
    return "\n".join(
        line[1:]
        for line in diff_text.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


class Retriever:
    def __init__(self) -> None:
        self.examples = all_examples()
        vecs = np.array([embed(e["code"]) for e in self.examples], dtype="float32")
        faiss.normalize_L2(vecs)
        self.index = faiss.IndexFlatIP(vecs.shape[1])
        self.index.add(vecs)

    def search(self, query: str, k: int = 3) -> list[dict]:
        if not query.strip():
            return []
        q = np.array([embed(query)], dtype="float32")
        faiss.normalize_L2(q)
        _, idx = self.index.search(q, min(k, len(self.examples)))
        return [self.examples[i] for i in idx[0] if i >= 0]

    def block(self, query: str, k: int = 3) -> str:
        """Formatted few-shot block to inject into the prompt, or '' on no hit."""
        hits = self.search(query, k)
        if not hits:
            return ""
        lines = ["Similar known bugs (reference only, may be unrelated):"]
        for e in hits:
            code = e["code"].replace("\n", " ; ")
            lines.append(f"- ({e['bug_class']}) `{code}` -> {e['hint']}")
        return "\n".join(lines)


if __name__ == "__main__":  # self-check: retrieval returns a relevant class
    r = Retriever()
    hits = r.search("for i in range(len(nums) + 1):\n    s += nums[i]", k=3)
    classes = [h["bug_class"] for h in hits]
    assert hits, "expected retrieval hits"
    assert "off_by_one" in classes, classes
    print(f"ok: top-{len(hits)} classes={classes}")
