# Company AI Backend

FastAPI-based backend application for Company AI platform.

## Project Structure

```
apps/company-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core configuration and utilities
│   │   └── db/           # Database models and setup
│   └── main.py           # Application entry point
├── logs/                 # Application and supervisor logs
├── venv/                 # Python virtual environment
├── supervisord.conf      # Supervisor configuration
├── requirements.txt      # Python dependencies
├── setup_supervisor.sh   # Supervisor setup script
├── PROJECT_REVIEW.md     # Detailed project review
└── SUPERVISOR_SETUP.md   # Supervisor setup guide
```

## Quick Start

### 1. Install Dependencies

```bash
cd /home/aiapp/apps/company-ai
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup Supervisor

```bash
./setup_supervisor.sh
```

Or manually:
```bash
sudo cp supervisord.conf /etc/supervisor/conf.d/company-ai.conf
sudo supervisorctl reread
sudo supervisorctl update
```

### 3. Start the Application

```bash
# Using supervisor
sudo supervisorctl start company-ai-backend

# Or manually
cd backend
source ../venv/bin/activate
python main.py
```

### 4. Verify

```bash
# Check status
sudo supervisorctl status company-ai-backend

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/health
```

## Configuration

- **Application Config:** `backend/app/core/config.py`
- **Database:** PostgreSQL (see `database_setup.md`)
- **Logging:** Configured in `backend/app/core/logging.py`
- **Supervisor:** `supervisord.conf`

## API Endpoints

- `GET /` - Root endpoint with app info
- `GET /health` - Health check endpoint

## Documentation

- **Project Review:** See `PROJECT_REVIEW.md`
- **Supervisor Setup:** See `SUPERVISOR_SETUP.md`
- **Database Setup:** See `/home/aiapp/database_setup.md`

## Process Management

The application is managed by Supervisor, which provides:
- Automatic restart on failure
- Process monitoring
- Log management
- Easy start/stop/restart commands

See `SUPERVISOR_SETUP.md` for detailed management instructions.

## Development

### Running in Development Mode

```bash
cd backend
source ../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Viewing Logs

```bash
# Application logs
tail -f logs/backend_stdout.log
tail -f logs/backend_stderr.log

# Supervisor logs
tail -f logs/supervisord.log
```

## Environment Variables

Create a `.env` file in the project root to override defaults:

```env
APP_NAME=company-ai
APP_VERSION=0.1.0
DATABASE_URL=postgresql+psycopg2://companyai_user:FTL@1234@localhost:5432/companyai
LOG_LEVEL=INFO
```

## Next Steps

1. Implement API routes in `backend/app/api/`
2. Create database models in `backend/app/db/`
3. Add database migrations (Alembic)
4. Implement authentication/authorization
5. Add API documentation
6. Set up CI/CD pipeline
