import ollama

EMBED_MODEL = "nomic-embed-text"


def embed(text: str) -> list[float]:
    return ollama.embeddings(model=EMBED_MODEL, prompt=text)["embedding"]
