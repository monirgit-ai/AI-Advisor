# Supervisor Setup Guide

## Overview

This project uses Supervisor to manage the Company AI backend application process. Supervisor provides:
- Automatic process restart on failure
- Process monitoring and logging
- Easy process management (start/stop/restart)
- Log rotation and management

## Installation

### Install Supervisor

```bash
sudo apt-get update
sudo apt-get install supervisor
```

Or using pip:
```bash
pip install supervisor
```

## Configuration

The supervisor configuration file is located at:
```
/home/aiapp/apps/company-ai/supervisord.conf
```

### Key Configuration Details

- **Program Name:** `company-ai-backend`
- **Command:** Runs uvicorn with 4 workers
- **User:** `aiapp`
- **Auto-restart:** Enabled
- **Logs Directory:** `/home/aiapp/apps/company-ai/logs/`

## Setup Steps

### 1. Create Logs Directory

```bash
mkdir -p /home/aiapp/apps/company-ai/logs
chown aiapp:aiapp /home/aiapp/apps/company-ai/logs
```

### 2. Install Dependencies

```bash
cd /home/aiapp/apps/company-ai
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Supervisor Configuration

**Option A: System-wide installation (recommended for production)**

```bash
sudo cp /home/aiapp/apps/company-ai/supervisord.conf /etc/supervisor/conf.d/company-ai.conf
sudo supervisorctl reread
sudo supervisorctl update
```

**Option B: User-level installation**

```bash
# Create supervisor config directory
mkdir -p ~/.config/supervisor/conf.d
cp /home/aiapp/apps/company-ai/supervisord.conf ~/.config/supervisor/conf.d/company-ai.conf

# Start supervisor with custom config
supervisord -c /home/aiapp/apps/company-ai/supervisord.conf
```

### 4. Start Supervisor

**System-wide:**
```bash
sudo systemctl start supervisor
sudo systemctl enable supervisor  # Enable on boot
```

**User-level:**
```bash
supervisord -c /home/aiapp/apps/company-ai/supervisord.conf
```

## Management Commands

### Using supervisorctl

```bash
# System-wide
sudo supervisorctl status
sudo supervisorctl start company-ai-backend
sudo supervisorctl stop company-ai-backend
sudo supervisorctl restart company-ai-backend
sudo supervisorctl tail company-ai-backend stdout
sudo supervisorctl tail company-ai-backend stderr

# User-level (if using custom config)
supervisorctl -c /home/aiapp/apps/company-ai/supervisord.conf status
supervisorctl -c /home/aiapp/apps/company-ai/supervisord.conf start company-ai-backend
```

### View Logs

```bash
# Application logs
tail -f /home/aiapp/apps/company-ai/logs/backend_stdout.log
tail -f /home/aiapp/apps/company-ai/logs/backend_stderr.log

# Supervisor logs
tail -f /home/aiapp/apps/company-ai/logs/supervisord.log
```

## Process Management

### Start All Services
```bash
sudo supervisorctl start company-ai:*
```

### Stop All Services
```bash
sudo supervisorctl stop company-ai:*
```

### Restart All Services
```bash
sudo supervisorctl restart company-ai:*
```

### Reload Configuration
```bash
sudo supervisorctl reread
sudo supervisorctl update
```

## Monitoring

### Check Process Status
```bash
sudo supervisorctl status company-ai-backend
```

Expected output:
```
company-ai-backend                RUNNING   pid 12345, uptime 0:05:23
```

### View Real-time Logs
```bash
sudo supervisorctl tail -f company-ai-backend stdout
```

## Troubleshooting

### Process Not Starting

1. Check supervisor logs:
   ```bash
   tail -f /home/aiapp/apps/company-ai/logs/supervisord.log
   ```

2. Check application logs:
   ```bash
   tail -f /home/aiapp/apps/company-ai/logs/backend_stderr.log
   ```

3. Verify configuration:
   ```bash
   sudo supervisorctl reread
   ```

### Process Keeps Restarting

1. Check stderr logs for errors:
   ```bash
   tail -f /home/aiapp/apps/company-ai/logs/backend_stderr.log
   ```

2. Verify dependencies are installed:
   ```bash
   source /home/aiapp/apps/company-ai/venv/bin/activate
   pip list
   ```

3. Test the application manually:
   ```bash
   cd /home/aiapp/apps/company-ai/backend
   source ../venv/bin/activate
   python main.py
   ```

## Configuration Customization

To modify the supervisor configuration:

1. Edit `/home/aiapp/apps/company-ai/supervisord.conf`
2. Reload supervisor:
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   ```

### Common Modifications

**Change number of workers:**
```ini
command=/home/aiapp/apps/company-ai/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 8
```

**Change port:**
```ini
command=/home/aiapp/apps/company-ai/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
```

**Add environment variables:**
```ini
environment=PYTHONPATH="/home/aiapp/apps/company-ai/backend",DATABASE_URL="postgresql://..."
```

## Notes

- Supervisor runs as the `aiapp` user
- Logs are automatically rotated (50MB max, 10 backups)
- Process auto-restarts on failure (max 3 retries)
- Application starts on port 8000 by default
- Health check available at: `http://localhost:8000/health`
