"""Load FAQ articles, embed them, store them in Atlas, create the index."""
import json
from pathlib import Path



from database import EMBEDDING_FIELD, ensure_vector_index, get_collection
from embeddings import embed_texts

DATA_FILE = Path(__file__).parent / "data" / "faq_articles.json"


def build_text(article: dict) -> str:
    """The text we embed: title + question + answer gives the best context."""
    return f"{article['title']}. {article['question']} {article['answer']}"


def main() -> None:
    articles = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(articles)} articles.")

    print("Generating embeddings...")
    vectors = embed_texts([build_text(a) for a in articles])
    for article, vector in zip(articles, vectors):
        article[EMBEDDING_FIELD] = vector

    collection = get_collection()
    collection.delete_many({})  # makes re-running the script safe
    collection.insert_many(articles)
    print(f"Inserted {len(articles)} documents.")

    ensure_vector_index(collection)


if __name__ == "__main__":
    main()
