# Step 6 Migration Instructions

## 1. Install Dependencies

```bash
cd /home/aiapp/apps/company-ai/backend
source ../venv/bin/activate
pip install -r requirements.txt
```

## 2. Verify Ollama is Running

```bash
# Check if Ollama is installed
ollama --version

# Start Ollama if not running
ollama serve

# Pull the embedding model
ollama pull nomic-embed-text
```

## 3. Ensure pgvector Extension is Enabled

```bash
# Connect to database and enable extension
psql -U companyai_user -d companyai -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## 4. Generate and Run Migration

```bash
cd /home/aiapp/apps/company-ai/backend
source ../venv/bin/activate

# Generate migration
alembic revision --autogenerate -m "Add document chunks and index status"

# Review the generated migration file in alembic/versions/
# It should include:
# - Adding index_status and index_error columns to documents table
# - Creating document_chunks table with vector(768) column

# Edit the migration file to add IVFFlat index after table creation:
# Add this in the upgrade() function after op.create_table('document_chunks', ...):
#
#   op.execute("""
#       CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
#       ON document_chunks 
#       USING ivfflat (embedding vector_cosine_ops) 
#       WITH (lists = 100);
#   """)

# Run migration
alembic upgrade head
```

## 5. Test the System

```bash
# 1. Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Login to get token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# 3. Upload a document (if not already done)
curl -X POST http://127.0.0.1:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_document.txt"

# 4. Index the document (get document_id from upload response)
curl -X POST http://127.0.0.1:8000/documents/{document_id}/index \
  -H "Authorization: Bearer $TOKEN"

# 5. Search
curl -X POST http://127.0.0.1:8000/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "top_k": 5}'
```

