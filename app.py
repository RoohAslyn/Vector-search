"""Web UI for the FAQ semantic search.

Run:
    python app.py
then open http://127.0.0.1:5000
"""
from flask import Flask, jsonify, render_template, request

from database import get_collection
from embeddings import get_model
from search import vector_search

app = Flask(__name__)

MAX_QUERY_LENGTH = 300
MAX_LIMIT = 10

_collection = None


def collection():
    """Connect to Atlas once and reuse the connection."""
    global _collection
    if _collection is None:
        _collection = get_collection()
    return _collection


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/categories")
def categories():
    try:
        return jsonify(sorted(collection().distinct("category")))
    except Exception as exc:  # network, auth, wrong URI, ...
        return jsonify({"error": f"Could not reach the database: {exc}"}), 500


@app.get("/api/search")
def search():
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip() or None

    try:
        limit = int(request.args.get("limit", 5))
    except ValueError:
        limit = 5
    limit = max(1, min(limit, MAX_LIMIT))

    if not query:
        return jsonify({"error": "Please type a question."}), 400
    if len(query) > MAX_QUERY_LENGTH:
        return jsonify({"error": f"Question is too long (max {MAX_QUERY_LENGTH} characters)."}), 400

    try:
        results = vector_search(collection(), query, limit, category)
    except Exception as exc:
        return jsonify({"error": f"Search failed: {exc}"}), 500

    for doc in results:
        doc["score"] = round(float(doc["score"]), 4)
    return jsonify({"query": query, "results": results})


if __name__ == "__main__":
    print("Loading embedding model (first run downloads ~90 MB)...")
    get_model()  # warm up so the first search is fast
    print("Open http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
