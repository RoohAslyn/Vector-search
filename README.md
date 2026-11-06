# MongoDB Atlas Vector Search – FAQ Semantic Search

A small Python app that finds the most relevant FAQ articles for a question by
**meaning**, not by keyword matching.

## How it works

1. **FAQ documents** – 50 articles in `data/faq_articles.json`.
2. **Embedding model** – `all-MiniLM-L6-v2` (free, local) turns text into 384-number vectors.
3. **MongoDB Atlas** – stores each article together with its vector in an `embedding` field.
4. **Vector Search** – a `vectorSearch` index lets `$vectorSearch` find nearest vectors.
5. **Python app** – embeds your query the same way and prints results ranked by similarity.

## Setup

1. Create a free **M0** cluster at https://cloud.mongodb.com.
2. Create a database user, and under *Network Access* allow your IP.
3. Click **Connect → Drivers**, copy the connection string into `.env`.
4. Install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. Load data and create the index (waits until the index is ready):

   ```bash
   python ingest.py
   ```

6. Search:

   ```bash
   python search.py "I forgot my password"
   python search.py "my parcel hasn't arrived" --limit 3
   python search.py "refund" --category Returns
   python search.py            # interactive mode
   ```

7. Or use the web UI:

   ```bash
   python app.py
   ```

   Then open http://127.0.0.1:5000. Type a question, pick a category, and see
   ranked results with a similarity bar. Example queries are one click away.

## Files

| File | Purpose |
|------|---------|
| `embeddings.py` | Loads the model, converts text to vectors |
| `database.py` | Connects to Atlas, creates the vector index |
| `ingest.py` | Reads JSON, embeds, inserts, builds index |
| `search.py` | Runs the `$vectorSearch` aggregation (command line) |
| `app.py` | Flask server: serves the UI and a JSON search API |
| `templates/index.html` | The search page (HTML, CSS and JavaScript in one file) |

## API

- `GET /api/search?q=<question>&category=<optional>&limit=<1-10>` returns ranked results as JSON.
- `GET /api/categories` returns the list of categories for the dropdown.

## Notes

- The index `numDimensions` (384) must match the model's output size. If you
  switch models, update `EMBEDDING_DIM` in `embeddings.py` and recreate the index.
- Never commit `.env`; add it to `.gitignore`.
- `numCandidates` controls accuracy vs. speed. Higher is more accurate but slower.
