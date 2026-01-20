# AI Advisor

An enterprise-grade AI assistant platform with RAG (Retrieval-Augmented Generation) capabilities for document-based question answering. Built as a full-stack application with a Next.js frontend and FastAPI backend.

## 🚀 Features

- **Document Management**: Upload, index, and manage enterprise documents
- **RAG-Powered Chat**: Ask questions about your documents with AI-powered responses and citations
- **Multi-Company Support**: Company-scoped data isolation and security
- **Hybrid Search**: Combines semantic (vector) and full-text search for better results
- **Enterprise Authentication**: JWT-based authentication with role-based access
- **Document Chunking**: Intelligent document chunking with heading detection
- **Citation Tracking**: Responses include citations to source documents

## 📁 Project Structure

This is a monorepo containing both frontend and backend applications:

```
.
├── apps/
│   ├── company-ai-frontend/    # Next.js 14 frontend application
│   │   ├── app/                # Next.js App Router pages
│   │   ├── components/         # React components
│   │   ├── lib/                # API client and utilities
│   │   └── types/              # TypeScript type definitions
│   └── company-ai/             # FastAPI backend application
│       └── backend/
│           ├── app/
│           │   ├── api/        # API endpoints
│           │   ├── core/       # Configuration and security
│           │   ├── db/         # Database models and migrations
│           │   └── services/   # Business logic (RAG, embeddings, etc.)
│           └── alembic/        # Database migrations
├── database_setup.md           # Database setup instructions
└── README.md                   # This file
```

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **ShadCN UI** components
- **Axios** for API communication

### Backend
- **FastAPI** (Python 3.10+)
- **PostgreSQL** with **pgvector** extension
- **Alembic** for database migrations
- **OpenAI** for embeddings and LLM
- **Supervisor** for process management

### Database
- **PostgreSQL 14+**
- **pgvector** for vector similarity search
- Full-text search capabilities

## 🚦 Quick Start

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.10+** and pip
- **PostgreSQL 14+** with pgvector extension
- **OpenAI API key** (or compatible embedding service)

### 1. Database Setup

Set up PostgreSQL database (see `database_setup.md` for details):

```bash
# Create database and user
sudo -u postgres psql -c "CREATE DATABASE companyai;"
sudo -u postgres psql -c "CREATE USER companyai_user WITH PASSWORD 'FTL@1234';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE companyai TO companyai_user;"
```

### 2. Backend Setup

```bash
cd apps/company-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Set up environment variables
cd backend
cp .env.example .env
# Edit .env and add your configuration (OpenAI API key, database URL, etc.)

# Run database migrations
alembic upgrade head

# Seed admin user (optional)
python scripts/seed_admin.py

# Start backend (development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or set up with Supervisor (production)
./setup_supervisor.sh
sudo supervisorctl start company-ai-backend
```

### 3. Frontend Setup

```bash
cd apps/company-ai-frontend

# Install dependencies
npm install

# Set up environment variables (optional)
cp .env.example .env.local
# Edit .env.local if you need to customize API URL

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000` and will connect to the backend at `http://localhost:8000`.

### 4. Access the Application

1. Open `http://localhost:3000` in your browser
2. Login with admin credentials (seeded via `seed_admin.py`)
3. Upload documents in the Documents section
4. Index documents to make them searchable
5. Start chatting and asking questions about your documents

## 📚 Documentation

- **[Frontend README](apps/company-ai-frontend/README.md)** - Frontend setup and development guide
- **[Backend README](apps/company-ai/README.md)** - Backend setup and API documentation
- **[Database Setup](database_setup.md)** - PostgreSQL database configuration
- **[Backend Project Review](apps/company-ai/PROJECT_REVIEW.md)** - Detailed backend architecture

## 🔐 Environment Variables

### Backend (`.env`)

```env
# Database
DATABASE_URL=postgresql+psycopg2://companyai_user:FTL@1234@localhost:5432/companyai

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_LLM_MODEL=gpt-4

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=company-ai
LOG_LEVEL=INFO
```

### Frontend (`.env.local` - optional)

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## 🔧 Development

### Backend Development

```bash
cd apps/company-ai/backend
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd apps/company-ai-frontend
npm run dev
```

### Database Migrations

```bash
cd apps/company-ai/backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📡 API Endpoints

### Authentication
- `POST /auth/login` - User login

### Chat
- `POST /chat` - Send message and get AI response with citations

### Documents
- `GET /documents` - List all documents
- `POST /documents/upload` - Upload a document
- `POST /documents/{id}/index` - Index a document for search
- `DELETE /documents/{id}` - Delete a document

### Health
- `GET /health` - Health check endpoint

See the [Backend README](apps/company-ai/README.md) for more details.

## 🏗️ Architecture

### RAG Pipeline

1. **Document Upload**: Documents are uploaded and stored
2. **Chunking**: Documents are split into chunks with heading detection
3. **Embedding**: Chunks are converted to vector embeddings
4. **Indexing**: Embeddings and metadata are stored in PostgreSQL with pgvector
5. **Query**: User queries are embedded and searched against document chunks
6. **Retrieval**: Relevant chunks are retrieved using hybrid search (vector + full-text)
7. **Generation**: LLM generates response using retrieved context with citations

### Security

- JWT-based authentication
- Company-scoped data isolation
- Role-based access control
- Secure document storage
- API token validation

## 🚢 Deployment

### Backend (Production)

The backend uses Supervisor for process management:

```bash
cd apps/company-ai
./setup_supervisor.sh
sudo supervisorctl start company-ai-backend
sudo supervisorctl status company-ai-backend
```

### Frontend (Production)

```bash
cd apps/company-ai-frontend
npm run build
npm start
```

Or deploy to Vercel/Netlify (Next.js recommended hosting).

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📝 License

This is a private enterprise application.

## 🆘 Troubleshooting

### Backend not starting
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database connection string in `.env`
- Check logs: `tail -f apps/company-ai/logs/backend_stdout.log`

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Check CORS settings in backend

### Database migration errors
- Ensure pgvector extension is installed: `CREATE EXTENSION IF NOT EXISTS vector;`
- Check database user has proper permissions
- Review migration files in `apps/company-ai/backend/alembic/versions/`

### Authentication issues
- Verify JWT secret key matches between frontend and backend
- Check token expiration settings
- Ensure user exists in database

## 📧 Support

For issues and questions, please contact the development team or create an issue in the repository.

---

**Built with ❤️ for enterprise AI applications**
