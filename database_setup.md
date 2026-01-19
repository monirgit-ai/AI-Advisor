# Database Setup Reference

## Database Configuration

**Database:** `companyai`  
**User:** `companyai_user`  
**Password:** `FTL@1234`  
**Privileges:** Full access granted

## Connection Details

- **Host:** localhost
- **Port:** 5432 (default)
- **Database:** companyai
- **User:** companyai_user
- **Password:** FTL@1234

## Connection String Format

```
postgresql://companyai_user:FTL@1234@localhost:5432/companyai
```

## Setup Commands (for reference)

```sql
CREATE DATABASE companyai;
CREATE USER companyai_user WITH PASSWORD 'FTL@1234';
GRANT ALL PRIVILEGES ON DATABASE companyai TO companyai_user;
```

## Access Method

To access PostgreSQL as postgres user:
```bash
echo -e "FTL@1234\nFTL@1234" | su - aiapp -c "sudo -S -u postgres psql"
```

## Notes

- PostgreSQL version: 14.20
- pgvector extension will be created in the application setup
- All operations performed as `aiapp` user with sudo access
