"""MongoDB Atlas connection and vector index management."""
import os
import time

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel

from embeddings import EMBEDDING_DIM

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "faq_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "faq_articles")
INDEX_NAME = os.getenv("VECTOR_INDEX_NAME", "faq_vector_index")
EMBEDDING_FIELD = "embedding"


def get_collection():
    if not MONGODB_URI or "<password>" in MONGODB_URI:
        raise SystemExit("Set a real MONGODB_URI in your .env file first.")
    client = MongoClient(MONGODB_URI)
    return client[DB_NAME][COLLECTION_NAME]


def ensure_vector_index(collection, wait: bool = True) -> None:
    """Create the vector search index if it does not exist yet."""
    existing = {idx["name"] for idx in collection.list_search_indexes()}
    if INDEX_NAME not in existing:
        model = SearchIndexModel(
            name=INDEX_NAME,
            type="vectorSearch",
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "path": EMBEDDING_FIELD,
                        "numDimensions": EMBEDDING_DIM,
                        "similarity": "cosine",
                    },
                    # Optional: lets us pre-filter results by category
                    {"type": "filter", "path": "category"},
                ]
            },
        )
        collection.create_search_index(model=model)
        print(f"Creating vector index '{INDEX_NAME}'...")

    if wait:
        print("Waiting for index to become queryable (can take ~1 minute)...")
        while True:
            indexes = list(collection.list_search_indexes(INDEX_NAME))
            if indexes and indexes[0].get("queryable"):
                print("Index is ready.")
                return
            time.sleep(5)
