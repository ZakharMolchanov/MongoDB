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

-- ===== Темы =====
INSERT INTO topics (title, description, difficulty) VALUES
('Mongo Basics', 'Базовые запросы find/projection/sort/limit', 'easy'),
('Aggregations I', 'Простые агрегаты с $match/$group', 'medium'),
('Aggregations II', 'Агрегации на пользователях и товарах', 'medium');

-- ===== Задания (Basics) =====
INSERT INTO assignments (topic_id, title, description, difficulty)
SELECT t.topic_id, 'Найди активные заказы', 'Верни все заказы со статусом "A". Отсортируй по _id (возрастание). Коллекция: orders', 'easy'
FROM topics t WHERE t.title='Mongo Basics';

INSERT INTO assignments (topic_id, title, description, difficulty)
SELECT t.topic_id, 'Пользователи старше 30 (проекция)', 'Найди пользователей с age > 30. Верни только name и city (без _id). Отсортируй по name.', 'easy'
FROM topics t WHERE t.title='Mongo Basics';

INSERT INTO assignments (topic_id, title, description, difficulty)
SELECT t.topic_id, 'Топ-2 дорогих товара', 'Выведи 2 самых дорогих товара (product, price). Отсортируй по price по убыванию. Коллекция: products', 'easy'
FROM topics t WHERE t.title='Mongo Basics';

-- ===== Задания (Aggregations I) =====
INSERT INTO assignments (topic_id, title, description, difficulty)
SELECT t.topic_id, 'Количество заказов по статусу', 'Сосчитай количество заказов по полю status. Верни документы вида {_id: <status>, count: <number>}. Отсортируй по _id.', 'medium'
FROM topics t WHERE t.title='Aggregations I';

INSERT INTO assignments (topic_id, title, description, difficulty)
SELECT t.topic_id, 'Средняя цена по категории', 'Посчитай среднюю цену товаров по категории. Верни {_id: <category>, avgPrice: <number>} с округлением не требуется. Отсортируй по _id.', 'medium'
FROM topics t WHERE t.title='Aggregations I';

INSERT INTO assignments (topic_id, title, description, difficulty)
SELECT t.topic_id, 'Сумма и средняя сумма заказов', 'Подсчитай total и avg по полю amount в orders. Верни один документ {_id: null, total: <sum>, avg: <avg>}.', 'medium'
FROM topics t WHERE t.title='Aggregations I';

-- ===== Задания (Aggregations II) =====
INSERT INTO assignments (topic_id, title, description, difficulty)
SELECT t.topic_id, 'Пользователи по городам', 'Сосчитай количество пользователей по city. Верни {_id: <city>, count: <n>} и отсортируй по _id.', 'medium'
FROM topics t WHERE t.title='Aggregations II';

INSERT INTO assignments (topic_id, title, description, difficulty)
SELECT t.topic_id, 'Количество товаров в наличии', 'Посчитай, сколько товаров in_stock=true по категориям. Верни {_id: <category>, count: <n>}. Отсортируй по _id.', 'medium'
FROM topics t WHERE t.title='Aggregations II';

INSERT INTO assignments (topic_id, title, description, difficulty)
SELECT t.topic_id, 'Мин/Макс цена', 'Найди минимальную и максимальную цену в products. Верни один документ {_id: null, min: <min>, max: <max>}.', 'medium'
FROM topics t WHERE t.title='Aggregations II';

-- ===== Тесты =====
-- 1) Basics: активные заказы
INSERT INTO assignment_tests (assignment_id, expected_result, test_description)
SELECT a.assignment_id,
       '[{"_id":"1","status":"A","amount":100},{"_id":"3","status":"A","amount":300}]'::jsonb,
       'Вернуть только заказы со статусом A, отсортировать по _id'
FROM assignments a WHERE a.title='Найди активные заказы';

-- 2) Basics: пользователи >30, только name/city, сорт по name
INSERT INTO assignment_tests (assignment_id, expected_result, test_description)
SELECT a.assignment_id,
       '[{"name":"Charlie","city":"Berlin"},{"name":"Diana","city":"London"}]'::jsonb,
       'age > 30, проекция {name:1, city:1, _id:0}, сорт по name'
FROM assignments a WHERE a.title='Пользователи старше 30 (проекция)';

-- 3) Basics: топ-2 по цене (desc)
INSERT INTO assignment_tests (assignment_id, expected_result, test_description)
SELECT a.assignment_id,
       '[{"product":"Laptop","price":1200},{"product":"Monitor","price":300}]'::jsonb,
       'две записи с наибольшей ценой'
FROM assignments a WHERE a.title='Топ-2 дорогих товара';

-- 4) Agg I: count по статусу
INSERT INTO assignment_tests (assignment_id, expected_result, test_description)
SELECT a.assignment_id,
       '[{"_id":"A","count":2},{"_id":"B","count":1}]'::jsonb,
       'group by status, сорт по _id'
FROM assignments a WHERE a.title='Количество заказов по статусу';

-- 5) Agg I: средняя цена по категории
INSERT INTO assignment_tests (assignment_id, expected_result, test_description)
SELECT a.assignment_id,
       '[{"_id":"Accessories","avgPrice":35},{"_id":"Electronics","avgPrice":750}]'::jsonb,
       'avg по price, сорт по _id'
FROM assignments a WHERE a.title='Средняя цена по категории';

-- 6) Agg I: сумма и средняя сумма заказов
INSERT INTO assignment_tests (assignment_id, expected_result, test_description)
SELECT a.assignment_id,
       '[{"_id":null,"total":600,"avg":200}]'::jsonb,
       'sum и avg по amount'
FROM assignments a WHERE a.title='Сумма и средняя сумма заказов';

-- 7) Agg II: пользователи по городам
INSERT INTO assignment_tests (assignment_id, expected_result, test_description)
SELECT a.assignment_id,
       '[{"_id":"Berlin","count":1},{"_id":"London","count":2},{"_id":"Paris","count":1}]'::jsonb,
       'group by city, сорт по _id'
FROM assignments a WHERE a.title='Пользователи по городам';

-- 8) Agg II: товары в наличии по категориям
INSERT INTO assignment_tests (assignment_id, expected_result, test_description)
SELECT a.assignment_id,
       '[{"_id":"Accessories","count":1},{"_id":"Electronics","count":2}]'::jsonb,
       'in_stock=true, group by category'
FROM assignments a WHERE a.title='Количество товаров в наличии';

-- 9) Agg II: min/max
INSERT INTO assignment_tests (assignment_id, expected_result, test_description)
SELECT a.assignment_id,
       '[{"_id":null,"min":25,"max":1200}]'::jsonb,
       'min/max по price'
FROM assignments a WHERE a.title='Мин/Макс цена';