-- Safe SQL to add missing columns/tables without dropping existing data.
-- Run these commands inside the running postgres container, e.g.:
-- docker-compose exec postgres psql -U postgres -d mydb -f /docker-entrypoint-initdb.d/migrations/add_missing_tables.sql

-- 1) Add 'is_admin' column to users if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='is_admin'
    ) THEN
        ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
    END IF;
END$$;

-- 2) Create request_logs table if missing
CREATE TABLE IF NOT EXISTS request_logs (
    id serial PRIMARY KEY,
    path varchar(512) NOT NULL,
    method varchar(10) NOT NULL,
    status_code integer,
    user_id integer,
    created_at timestamp without time zone DEFAULT now(),
    payload text
);

-- 3) Ensure queries table exists with FK to users(id) - only add FK if users table exists
CREATE TABLE IF NOT EXISTS queries (
    query_id serial PRIMARY KEY,
    user_id integer,
    assignment_id integer NOT NULL,
    query_text text NOT NULL,
    status varchar(50) NOT NULL,
    result jsonb,
    error_message text,
    error_json jsonb,
    exec_ms integer,
    result_count integer,
    created_at timestamp without time zone DEFAULT now()
);

-- Add FK to users if users table exists and FK not present
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='users') THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
            WHERE tc.table_name='queries' AND tc.constraint_type='FOREIGN KEY' AND kcu.column_name='user_id'
        ) THEN
            ALTER TABLE queries ADD CONSTRAINT queries_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
        END IF;
    END IF;
END$$;

-- Optional: if assignments.schema_json column type needs check, it's JSON; ensure it exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='assignments' AND column_name='schema_json'
    ) THEN
        ALTER TABLE assignments ADD COLUMN schema_json jsonb;
    END IF;
END$$;

-- End of migration SQL
