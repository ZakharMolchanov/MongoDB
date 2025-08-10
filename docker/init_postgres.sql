-- ==========================
-- Таблица пользователей
-- ==========================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ==========================
-- Темы (Topics)
-- ==========================
CREATE TABLE IF NOT EXISTS topics (
    topic_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ==========================
-- Задания (Assignments)
-- ==========================
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES topics(topic_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ==========================
-- Тесты к заданиям (Assignment_Tests)
-- expected_result в JSONB
-- ==========================
CREATE TABLE IF NOT EXISTS assignment_tests (
    test_id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    expected_result JSONB NOT NULL,
    test_description TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ==========================
-- Выполненные задания (Completed_Assignments)
-- ==========================
CREATE TABLE IF NOT EXISTS completed_assignments (
    completed_assignment_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assignment_id INTEGER NOT NULL REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    completion_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT completed_unique UNIQUE (user_id, assignment_id)
);

-- ==========================
-- История отправок решений (Queries)
-- result в JSONB, метрики, корректный FK
-- ==========================
CREATE TABLE IF NOT EXISTS queries (
    query_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assignment_id INTEGER NOT NULL REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('ok','failed','error')),
    result JSONB,
    error_message TEXT,
    error_json JSONB,
    exec_ms INT,
    result_count INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ==========================
-- Индексы
-- ==========================
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_assignments_topic_id ON assignments(topic_id);
CREATE INDEX IF NOT EXISTS idx_assignment_tests_assignment_id ON assignment_tests(assignment_id);
CREATE INDEX IF NOT EXISTS idx_completed_assignments_user_id ON completed_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries(user_id);
CREATE INDEX IF NOT EXISTS idx_queries_assignment_id ON queries(assignment_id);

-- ==========================
-- ТЕСТОВЫЕ ДАННЫЕ (без хардкода id = 1)
-- ==========================
WITH t AS (
  INSERT INTO topics (title, description, difficulty)
  VALUES ('Mongo Basics', 'Простые операции find', 'easy')
  RETURNING topic_id
),
a AS (
  INSERT INTO assignments (topic_id, title, description, difficulty)
  SELECT t.topic_id, 'Найди активные заказы', 'Выбери все заказы со статусом "A"', 'easy'
  FROM t
  RETURNING assignment_id
)
INSERT INTO assignment_tests (assignment_id, expected_result, test_description)
SELECT
  a.assignment_id,
  '[{"_id": "1", "status": "A", "amount": 100}, {"_id": "3", "status": "A", "amount": 300}]'::jsonb,
  'Должны вернуться только заказы со статусом "A", в порядке по _id'
FROM a;
