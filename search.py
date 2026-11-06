"""Semantic search over the FAQ collection using $vectorSearch.

Usage:
    python search.py "how do I get my money back"
    python search.py "my package is late" --category Shipping --limit 3
    python search.py            # interactive mode
"""
import argparse

from database import EMBEDDING_FIELD, INDEX_NAME, get_collection
from embeddings import embed_query


def vector_search(collection, query: str, limit: int = 5, category: str | None = None):
    stage = {
        "index": INDEX_NAME,
        "path": EMBEDDING_FIELD,
        "queryVector": embed_query(query),
        "numCandidates": max(100, limit * 20),  # how many neighbours ANN considers
        "limit": limit,
    }
    if category:
        stage["filter"] = {"category": category}

    pipeline = [
        {"$vectorSearch": stage},
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "category": 1,
                "title": 1,
                "question": 1,
                "answer": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]
    return list(collection.aggregate(pipeline))


def print_results(results: list[dict]) -> None:
    if not results:
        print("No results found.\n")
        return
    for rank, doc in enumerate(results, start=1):
        print(f"{rank}. [{doc['score']:.3f}] {doc['title']}  ({doc['category']})")
        print(f"   Q: {doc['question']}")
        print(f"   A: {doc['answer']}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Semantic FAQ search")
    parser.add_argument("query", nargs="?", help="your question")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--category", default=None)
    args = parser.parse_args()

    collection = get_collection()

    if args.query:
        print_results(vector_search(collection, args.query, args.limit, args.category))
        return

    print("Type a question (or 'quit' to exit).")
    while True:
        query = input("\nSearch> ").strip()
        if query.lower() in {"quit", "exit", "q"}:
            break
        if query:
            print_results(vector_search(collection, query, args.limit, args.category))


if __name__ == "__main__":
    main()
