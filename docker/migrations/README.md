Run these commands from PowerShell on the host to apply safe DB fixes to the running Postgres container.

1) Copy the migration SQL into the container and execute via psql (recommended):

```powershell
# Copy migration file into container (optional if volume already mounts it under /docker-entrypoint-initdb.d)
# Then run:
docker-compose exec postgres bash -lc "psql -U postgres -d mydb -f /docker-entrypoint-initdb.d/migrations/add_missing_tables.sql"
```

2) If you prefer to run statements interactively:

```powershell
docker-compose exec postgres psql -U postgres -d mydb
# then in psql run the needed SQL, e.g.:
# ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;
# CREATE TABLE IF NOT EXISTS request_logs (...);
# ALTER TABLE queries ADD CONSTRAINT ...;
```

3) After applying migrations, restart services to ensure they pick up code changes (on host PowerShell):

```powershell
# Rebuild affected services and restart
docker-compose up -d --build auth-service core-service frontend
# Check logs
docker-compose logs -f auth-service core-service frontend
```

Notes:
- The migration SQL is written to avoid dropping data. It attempts to add missing columns/tables and add FK only if users table exists.
- If your Postgres data directory uses an older schema incompatible with the code (e.g. different column names), consider creating a DB backup before making changes:

```powershell
docker-compose exec postgres pg_dump -U postgres -Fc mydb > backup_mydb.dump
```

If you want, I can run these commands for you (I will not run them without confirmation).

Seeding MongoDB (if `docker/init_mongo.js` did not run because the container was initialized previously):

```powershell
# Run the helper script to seed sample collections if they are empty
.\n+\docker\migrations\seed_mongo.ps1
```