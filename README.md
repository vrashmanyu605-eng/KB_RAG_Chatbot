# FastAPI knowledge-base starter

FastAPI document ingestion and retrieval using PostgreSQL/pgvector, Gemini embeddings, and LiteLLM for model-provider-agnostic chat and judging.

## Run locally

1. Create and activate a virtual environment, then install dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Start PostgreSQL with pgvector:

   ```powershell
   docker compose up -d db
   ```

   The Compose file publishes PostgreSQL on host port `5433` to avoid colliding with a PostgreSQL server already using `5432`. If you change the published port, make the same change in `DATABASE_URL`.

3. If `.env` does not already exist, copy `.env.example` to `.env`; otherwise, add or update the required settings without overwriting unrelated values. The database username, password, and database name in `DATABASE_URL` must match `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` in Compose. `POSTGRES_PASSWORD` is used when PostgreSQL initializes a new data volume; changing it later does not change the password in an existing database. For an existing volume, update the role password in PostgreSQL and set the same password in `DATABASE_URL`.

   Set `GOOGLE_API_KEY` and choose the LiteLLM model and its provider credentials. For example, `gemini/gemini-2.5-flash` uses Gemini; LiteLLM accepts other model/provider prefixes as well.

4. Run the API:

   ```powershell
   uvicorn app.main:app --reload
   ```

   The API creates the `vector` extension and its table on startup. Interactive API docs are at <http://127.0.0.1:8000/docs>.

## API

### Upload Markdown or text files

Upload one or more UTF-8 `.md`/`.txt` files as multipart form data:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/documents `
  -F "files=@kb/KB-001_password_reset.md"
```

Optional YAML front matter is saved as metadata for every chunk:

```yaml
---
doc_id: KB-001
title: Password reset
status: current
owner: Identity & Access
---
Document body...
```

Documents with `status: unverified` (case-insensitive) are reported as skipped and are not embedded or stored. Other statuses, including `deprecated`, are ingested and retained as metadata. Re-uploading a document with the same `doc_id` replaces its previous chunks; files without a `doc_id` use their filename.

### Ask a question

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/chat `
  -H "Content-Type: application/json" `
  -d '{"question":"How long does an account stay locked?"}'
```

The response contains the model answer and source chunks with their metadata. `top_k` can optionally control the number of retrieved chunks. The system prompt instructs the model to treat the question, document contents, and metadata as untrusted data, ignore embedded instructions, use only retrieved evidence, cite document IDs, and report gaps or conflicts instead of guessing.

Prompt instructions reduce prompt-injection and hallucination risk but cannot guarantee that a model will always follow them. Keep provider credentials out of document content, limit access to the API, and review model answers for high-impact use.

### Evaluate an answer

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/evaluations `
  -H "Content-Type: application/json" `
  -d '{"question":"How long does an account stay locked?","answer":"30 minutes."}'
```

The judge scores relevance, recall, and precision from 0 to 5 and returns rationales. If `contexts` is omitted, the API retrieves evidence from the vector store; otherwise, it evaluates against the supplied context strings. Set `JUDGE_MODEL` to use a different LiteLLM model for evaluation. The judge prompt also treats all request fields as untrusted evaluation data and instructs the judge not to obey embedded instructions or use outside knowledge.

`GET /health` is a basic process health check. LLM and embedding providers require their respective API keys at runtime; provider failures are surfaced by FastAPI rather than being replaced with fallback answers.

## Tests

```powershell
pytest
```
