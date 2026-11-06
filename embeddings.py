"""Turns text into numerical vectors using a free, local model.

all-MiniLM-L6-v2 produces 384-dimensional vectors, runs on CPU, and
needs no API key. The first run downloads the model (~90 MB).
"""
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # must match numDimensions in the vector index

_model = None


def get_model() -> SentenceTransformer:
    """Load the model once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed many texts at once (faster than one by one)."""
    vectors = get_model().encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    )
    return vectors.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single search query."""
    return embed_texts([query])[0]
