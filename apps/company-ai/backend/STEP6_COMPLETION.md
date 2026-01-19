# STEP 6 COMPLETION NOTE — RAG Indexing + Semantic Search

**Date:** 2026-01-17  
**Status:** ✅ COMPLETE  
**Phase:** RAG Indexing + Semantic Search (Phase-1 MVP)

---

## ✅ IMPLEMENTATION SUMMARY

Step 6 has been successfully completed. All required components for document chunking, embedding generation, vector storage, and semantic search are implemented and ready for testing.

**This step transforms the system into an AI-powered RAG (Retrieval-Augmented Generation) platform.**

---

## 📋 COMPLETED COMPONENTS

### 1. Configuration Updates ✅

**Location:** `app/core/config.py`

- **OLLAMA_BASE_URL:** `http://127.0.0.1:11434` (configurable via env)
- **OLLAMA_EMBED_MODEL:** `nomic-embed-text` (768-dimensions)
- All settings environment-configurable

### 2. Database Models ✅

#### A) DocumentChunk Model (`app/db/models/document_chunk.py`)

**Schema:**
- `id` (UUID, primary key, indexed)
- `company_id` (FK → companies.id, indexed) - Multi-tenant isolation
- `document_id` (FK → documents.id, indexed)
- `chunk_index` (int) - Order of chunk in document
- `text` (TEXT) - Chunk content
- `token_estimate` (int, nullable) - Simple estimate (~4 chars/token)
- `embedding` (Vector(768)) - **Fixed 768 dimensions for nomic-embed-text**
- `created_at` (timestamp)

**Relationships:**
- `company` → Company model
- `document` → Document model

#### B) Document Model Updates (`app/db/models/document.py`)

**Added Fields:**
- `index_status` (enum: `not_indexed`, `indexing`, `indexed`, `failed`)
- `index_error` (Text, nullable) - Error message if indexing fails

**New Enum:**
- `IndexStatus` - Tracks document indexing state

### 3. Chunking Service ✅

**Location:** `app/services/chunking.py`

**Function:** `chunk_text(text, chunk_size=1000, overlap=150)`

**Features:**
- **Chunk Size:** Default 1000 characters (configurable 800-1200 range)
- **Overlap:** Default 150 characters (configurable 100-200 range)
- **Smart Splitting:**
  - Primary: Split by paragraphs (double newline)
  - Fallback: Split by sentences
  - Final fallback: Split by words (for very long sentences)
- **Overlap Handling:** Preserves context between chunks
- **Size Enforcement:** Ensures all chunks within limits

**Algorithm:**
1. Try paragraph-based splitting first
2. For oversized paragraphs, use sentence splitting
3. For oversized sentences, use word splitting
4. Maintain overlap from previous chunk
5. Filter out empty chunks

### 4. Embeddings Service ✅

**Location:** `app/services/embeddings.py`

**Class:** `OllamaEmbedder`

**Features:**
- Calls Ollama `/api/embed` endpoint
- Model: `nomic-embed-text` (768 dimensions)
- Single text embedding: `embed(text) -> List[float]`
- Batch embedding: `embed_batch(texts) -> List[List[float]]`
- Error handling with logging
- Timeout: 60 seconds per request
- Dimension validation

**API Call Format:**
```python
POST http://127.0.0.1:11434/api/embed
Body: {"model": "nomic-embed-text", "input": "<text>"}
Response: {"embedding": [<768 floats>]}
```

### 5. Indexing Service ✅

**Location:** `app/services/indexer.py`

**Function:** `index_document(document_id, company_id, db) -> (success, error, chunks_created)`

**Pipeline:**
1. **Load Document:** Verify exists and belongs to company
2. **Check Text:** Ensure `text_extracted` exists
3. **Update Status:** Set `index_status = "indexing"`
4. **Delete Existing:** Remove old chunks for this document
5. **Chunk Text:** Split into overlapping chunks
6. **Generate Embeddings:** Batch embed all chunks via Ollama
7. **Store Chunks:** Create DocumentChunk records with vectors
8. **Update Status:** Set to `indexed` or `failed`
9. **Error Handling:** Capture errors in `index_error` field

**Features:**
- Synchronous processing (MVP approach)
- Company-scoped validation
- Robust error handling
- Status tracking throughout process
- Chunk deduplication (delete before re-index)

### 6. Search API Endpoint ✅

**Location:** `app/api/search.py`

#### POST /search

**Request:**
```json
{
  "query": "search text",
  "top_k": 5,
  "document_id": "optional-uuid"  // Optional filter
}
```

**Response:**
```json
{
  "results": [
    {
      "chunk_id": "...",
      "document_id": "...",
      "chunk_index": 0,
      "text": "chunk text...",
      "similarity_score": 0.95,
      "document_filename": "...",
      "token_estimate": 250
    }
  ],
  "total_results": 5
}
```

**Features:**
- **JWT Authentication:** Required via `get_current_user`
- **Company Scoping:** Only searches user's company documents
- **Cosine Similarity:** Uses pgvector `<=>` operator
- **Vector Search:** Embeds query, compares with stored embeddings
- **Optional Filtering:** Can filter by `document_id`
- **Top-K Results:** Configurable (1-50, default 5)
- **Similarity Scores:** Returns cosine similarity (0-1 range)
- **Document Context:** Includes source document filename

**Implementation:**
- Uses raw SQL with pgvector operators for performance
- `1 - (embedding <=> query_vec)` for cosine similarity
- ORDER BY similarity DESC
- JOIN with documents table for filename lookup

### 7. Document Indexing Endpoint ✅

**Location:** `app/api/documents.py`

#### POST /documents/{document_id}/index

**Features:**
- **JWT Authentication:** Required
- **Company Validation:** Ensures document belongs to user's company
- **Triggers Indexing:** Calls `index_document()` service
- **Status Updates:** Returns current index status

**Response:**
```json
{
  "document_id": "...",
  "status": "indexed",
  "chunks_created": 15,
  "index_status": "indexed"
}
```

### 8. Dependencies ✅

**Location:** `requirements.txt`

**Added:**
- `requests` - For Ollama API calls
- `pgvector` - PostgreSQL vector extension support

**Status:** All dependencies listed and ready for installation

### 9. API Wiring ✅

**Location:** `app/api/__init__.py`

- Search router included in main `api_router`
- Prefix: `/search`
- Tag: `search`

**API Structure:**
```
/api
  ├── /auth (authentication)
  ├── /documents (document management + indexing)
  ├── /search (semantic search)
  └── /health (health check)
```

---

## 🔐 SECURITY FEATURES

### Authentication
- ✅ JWT token required for all endpoints
- ✅ Token validated on every request
- ✅ User must be active

### Company Isolation
- ✅ All chunks scoped by `company_id`
- ✅ Search results filtered by user's company
- ✅ Indexing validates company ownership
- ✅ Cross-company access blocked

### Data Privacy
- ✅ All embeddings generated locally (Ollama)
- ✅ No external API calls for embeddings
- ✅ Documents never leave the server
- ✅ Vector data stored in company's database

---

## 🗄️ DATABASE REQUIREMENTS

### pgvector Extension

**Required:** PostgreSQL with pgvector extension enabled

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### IVFFlat Index (Recommended)

For fast similarity search, create IVFFlat index:

```sql
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
ON document_chunks 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

**Note:** Index creation happens in migration (manual step required)

**Tuning Note:** `lists = 100` is fine for MVP. When document chunks exceed 100k, consider tuning the `lists` parameter or migrating to HNSW index for better performance at scale.

### Vector Column

- **Type:** `vector(768)` - Fixed dimension
- **Model:** nomic-embed-text (768 dimensions)
- **Operator Class:** `vector_cosine_ops` for cosine similarity

---

## 🤖 OLLAMA REQUIREMENTS

### Installation

Ollama must be installed and running on the server:

```bash
# Check installation
ollama --version

# Start server (if not running)
ollama serve

# Pull embedding model
ollama pull nomic-embed-text
```

### Model Specifications

- **Model:** `nomic-embed-text`
- **Dimensions:** 768
- **API Endpoint:** `http://127.0.0.1:11434/api/embed`
- **Format:** JSON request/response

### Performance Considerations

- **Embedding Time:** ~50-200ms per chunk (CPU-dependent)
- **Batch Processing:** Sequential for MVP (can be parallelized later)
- **Timeout:** 60 seconds per request
- **Memory:** Model requires ~500MB RAM

---

## 📊 INDEXING PIPELINE

### Flow Diagram

```
Document (text_extracted)
    ↓
Chunk Text (1000 chars, 150 overlap)
    ↓
Generate Embeddings (Ollama API)
    ↓
Store Chunks + Vectors (PostgreSQL)
    ↓
Update Document Status (indexed/failed)
```

### Status Tracking

1. **not_indexed** - Initial state
2. **indexing** - Process started
3. **indexed** - Successfully completed
4. **failed** - Error occurred (see `index_error`)

### Error Handling

- Failed embeddings: Logged, chunk skipped
- API errors: Captured in `index_error`
- Partial failures: Some chunks indexed, error logged
- Re-indexing: Deletes old chunks before creating new ones

---

## 🧪 TESTING STATUS

### ✅ Code Implementation

- [x] All models created
- [x] All services implemented
- [x] All endpoints created
- [x] API routers wired
- [x] Dependencies added
- [x] Error handling in place

### ⏳ Pending (Requires Migration + Ollama)

- [ ] Database migration generated and applied
- [ ] pgvector extension enabled
- [ ] IVFFlat index created
- [ ] Ollama model pulled
- [ ] End-to-end testing (upload → index → search)

### Test Flow

1. **Upload Document:**
   ```bash
   POST /documents/upload
   → Returns document_id
   ```

2. **Index Document:**
   ```bash
   POST /documents/{document_id}/index
   → Creates chunks, generates embeddings, stores vectors
   → Returns chunks_created count
   ```

3. **Search:**
   ```bash
   POST /search
   Body: {"query": "search text", "top_k": 5}
   → Returns top chunks with similarity scores
   ```

---

## 🔧 TECHNICAL NOTES

### Chunking Strategy

- **Primary:** Paragraph-based (preserves context)
- **Fallback:** Sentence-based (for long paragraphs)
- **Final:** Word-based (for long sentences)
- **Overlap:** 150 chars ensures context continuity

### Embedding Generation

- **Model:** nomic-embed-text (768-dim, CPU-optimized)
- **API:** Synchronous calls (MVP approach)
- **Error Handling:** Graceful degradation (skips failed chunks)
- **Validation:** Dimension checking (must be 768)

### Vector Search

- **Similarity:** Cosine similarity (1 - cosine distance)
- **Index:** IVFFlat for fast approximate search
- **Query:** Embed query text, compare with stored vectors
- **Filtering:** Company-scoped + optional document filter

### Performance Considerations

**MVP (Current):**
- Synchronous processing
- Sequential embedding generation
- IVFFlat index with `lists = 100` (good enough for MVP)
- Clean abstraction for batch embedding (ready for parallelization)

**Future Optimizations (Step 8+):**
- **IVFFlat Tuning:** When chunks > 100k, tune `lists` parameter or migrate to HNSW
- **Parallel Embedding:** Use Celery/background workers for batch processing
- **HNSW Index:** Faster, more accurate for large-scale deployments
- **Async Indexing:** Background processing pipeline
- **Batch Operations:** Optimize for bulk indexing

**Design Note:** Current implementation keeps it simple for MVP. Clean abstractions allow future parallelization without major refactoring.

---

## 📁 PROJECT STRUCTURE

```
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py          # ✓ Includes search router
│   │   ├── auth.py
│   │   ├── deps.py
│   │   ├── documents.py         # ✓ Includes index endpoint
│   │   ├── search.py            # ✓ Semantic search endpoint
│   │   └── health.py
│   ├── core/
│   │   ├── config.py            # ✓ Ollama settings
│   │   ├── logging.py
│   │   └── security.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chunking.py          # ✓ Text chunking service
│   │   ├── embeddings.py        # ✓ Ollama embedder
│   │   └── indexer.py           # ✓ Document indexing orchestration
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   │       ├── __init__.py      # ✓ Exports DocumentChunk
│   │       ├── company.py
│   │       ├── user.py
│   │       ├── document.py      # ✓ Added index_status/error
│   │       └── document_chunk.py # ✓ Vector storage model
│   └── ...
├── alembic/
│   ├── env.py                   # ✓ Imports DocumentChunk
│   └── versions/                # Migration to be generated
└── requirements.txt             # ✓ Added requests, pgvector
```

---

## 🚀 NEXT STEPS

### Immediate (Required for Testing)

1. **Enable pgvector Extension:**
   ```bash
   psql -U companyai_user -d companyai -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

2. **Install Ollama Model:**
   ```bash
   ollama pull nomic-embed-text
   ```

3. **Generate Migration:**
   ```bash
   alembic revision --autogenerate -m "Add document chunks and index status"
   ```

4. **Add IVFFlat Index:**
   Edit migration file to include:
   ```sql
   CREATE INDEX document_chunks_embedding_idx 
   ON document_chunks 
   USING ivfflat (embedding vector_cosine_ops) 
   WITH (lists = 100);
   ```

5. **Run Migration:**
   ```bash
   alembic upgrade head
   ```

### Ready For (Step 7+)

- LLM answer generation
- Chat UI integration
- Prompt orchestration
- Agent logic
- Context window management

### Not Yet Implemented (As Per Requirements)

- ❌ Chunking strategies beyond basic overlap
- ❌ Multiple embedding models
- ❌ HNSW index (using IVFFlat for MVP)
- ❌ Async indexing pipeline
- ❌ Embedding caching
- ❌ Query result reranking

---

## ✅ VERIFICATION CHECKLIST

- [x] Configuration updated with Ollama settings
- [x] DocumentChunk model created with vector(768)
- [x] Document model updated with index_status/error
- [x] Chunking service implemented
- [x] Embeddings service implemented (Ollama)
- [x] Indexing service implemented
- [x] Search endpoint created
- [x] Index endpoint added to documents router
- [x] All dependencies added to requirements.txt
- [x] API routers wired correctly
- [ ] Database migration generated (pending)
- [ ] pgvector extension enabled (pending)
- [ ] IVFFlat index created (pending)
- [ ] Ollama model installed (pending)
- [ ] End-to-end testing completed (pending)

---

## 📝 COMMANDS FOR TESTING

### 1. Setup

```bash
# Install dependencies
cd /home/aiapp/apps/company-ai/backend
source ../venv/bin/activate
pip install -r requirements.txt

# Enable pgvector
psql -U companyai_user -d companyai -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Pull Ollama model
ollama pull nomic-embed-text
```

### 2. Generate and Run Migration

```bash
# Generate migration
alembic revision --autogenerate -m "Add document chunks and index status"

# Edit migration file to add IVFFlat index (see MIGRATION_INSTRUCTIONS.md)

# Run migration
alembic upgrade head
```

### 3. Test Flow

```bash
# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 1. Login
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# 2. Upload document
curl -X POST http://127.0.0.1:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_document.txt"

# 3. Index document (use document_id from upload response)
curl -X POST http://127.0.0.1:8000/documents/{document_id}/index \
  -H "Authorization: Bearer $TOKEN"

# 4. Search
curl -X POST http://127.0.0.1:8000/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query text", "top_k": 5}'
```

---

## 🎯 SUMMARY

**Step 6 is code-complete and ready for migration + testing.**

All RAG indexing and semantic search components are:
- ✅ Implemented
- ✅ Documented
- ✅ Ready for integration

The system can now:
- Chunk documents with overlap-aware splitting
- Generate embeddings locally via Ollama
- Store vectors in PostgreSQL pgvector
- Perform semantic search with cosine similarity
- Maintain company-scoped isolation throughout

**Key Achievements:**
- AI-powered RAG infrastructure complete
- Local-only embeddings (privacy-preserving)
- Multi-tenant vector storage
- Semantic search with similarity scores
- Status tracking for indexing pipeline

**Status:** ✅ CODE COMPLETE - PENDING MIGRATION + OLLAMA SETUP

**Next:** Generate migration, enable pgvector, pull Ollama model, test end-to-end flow.

---

**Prepared by:** AI Assistant  
**Reviewed by:** [Supervisor]  
**Date:** 2026-01-17
