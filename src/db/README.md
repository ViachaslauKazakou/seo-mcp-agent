# Database Documentation

PostgreSQL база данных для SEO MCP Agent с поддержкой pgvector для векторного поиска.

## 📊 Схема базы данных

### 🌐 Websites
Основная информация о сайтах и доступе к ним.

```sql
CREATE TABLE websites (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    description TEXT,
    
    -- Repository info
    repo_url VARCHAR(500),
    repo_path VARCHAR(500),
    repo_branch VARCHAR(100) DEFAULT 'main',
    
    -- SSH access
    ssh_host VARCHAR(255),
    ssh_port INTEGER DEFAULT 22,
    ssh_user VARCHAR(100),
    ssh_key_path VARCHAR(500),
    
    -- Settings
    language VARCHAR(10) DEFAULT 'en',
    country VARCHAR(10),
    is_active BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Назначение:** Хранит конфигурацию сайтов, включая доступ к репозиторию и хостингу через SSH.

---

### 📈 Analysis Runs
Метаданные о запусках анализа семантики.

```sql
CREATE TABLE analysis_runs (
    id SERIAL PRIMARY KEY,
    website_id INTEGER REFERENCES websites(id) ON DELETE CASCADE,
    
    status VARCHAR(20) DEFAULT 'pending',  -- pending, running, completed, failed
    fetcher_type VARCHAR(20) DEFAULT 'httpx',  -- httpx, playwright
    
    urls TEXT[],
    pages_analyzed INTEGER DEFAULT 0,
    
    -- Settings
    embedding_provider VARCHAR(50) DEFAULT 'hf',
    embedding_model VARCHAR(100),
    max_keywords INTEGER DEFAULT 100,
    num_clusters INTEGER DEFAULT 10,
    
    -- Summary
    total_keywords INTEGER DEFAULT 0,
    total_clusters INTEGER DEFAULT 0,
    intent_summary JSONB,
    
    error_message TEXT,
    
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

**Назначение:** Хранит информацию о каждом запуске анализа, настройки и результаты.

---

### 🔑 Keywords
Извлечённые ключевые слова с метриками.

```sql
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    analysis_run_id INTEGER REFERENCES analysis_runs(id) ON DELETE CASCADE,
    cluster_id INTEGER REFERENCES keyword_clusters(id) ON DELETE SET NULL,
    
    keyword VARCHAR(500) NOT NULL,
    intent VARCHAR(20) NOT NULL,  -- informational, commercial, navigational, transactional
    
    tf_idf_score FLOAT NOT NULL,
    frequency INTEGER DEFAULT 1,
    
    embedding FLOAT[],  -- Vector embedding для similarity search
    source_urls TEXT[],
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON keywords(analysis_run_id, intent);
CREATE INDEX ON keywords(analysis_run_id, tf_idf_score);
CREATE INDEX ON keywords(keyword);
```

**Назначение:** Хранит все извлечённые ключевые слова с TF-IDF метриками и embeddings.

---

### 🗂️ Keyword Clusters
Семантические кластеры ключевых слов.

```sql
CREATE TABLE keyword_clusters (
    id SERIAL PRIMARY KEY,
    analysis_run_id INTEGER REFERENCES analysis_runs(id) ON DELETE CASCADE,
    
    cluster_label INTEGER NOT NULL,
    cluster_name VARCHAR(500),
    
    -- Statistics
    size INTEGER DEFAULT 0,
    avg_tfidf_score FLOAT,
    top_keywords TEXT[],
    intent_distribution JSONB,
    
    centroid_embedding FLOAT[],  -- Центроид кластера
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON keyword_clusters(analysis_run_id, cluster_label);
```

**Назначение:** Группирует семантически связанные ключевые слова с статистикой.

---

### 🔍 SERP Results
Результаты анализа поисковой выдачи Google.

```sql
CREATE TABLE serp_results (
    id SERIAL PRIMARY KEY,
    
    query VARCHAR(500) NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    country VARCHAR(10) DEFAULT 'US',
    
    total_results INTEGER,
    featured_snippet JSONB,
    people_also_ask JSONB[],
    related_searches TEXT[],
    top_results JSONB[],
    
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON serp_results(query, fetched_at);
```

**Назначение:** Хранит snapshot поисковой выдачи для анализа конкурентов.

---

### 📍 SERP Positions
Отслеживание позиций сайта в выдаче.

```sql
CREATE TABLE serp_positions (
    id SERIAL PRIMARY KEY,
    website_id INTEGER REFERENCES websites(id) ON DELETE CASCADE,
    serp_result_id INTEGER REFERENCES serp_results(id) ON DELETE CASCADE,
    
    position INTEGER,
    url VARCHAR(1000) NOT NULL,
    title VARCHAR(500),
    snippet TEXT,
    
    is_featured BOOLEAN DEFAULT false,
    in_top_10 BOOLEAN DEFAULT false,
    in_top_3 BOOLEAN DEFAULT false,
    
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON serp_positions(website_id, checked_at);
CREATE INDEX ON serp_positions(serp_result_id, position);
```

**Назначение:** Отслеживает позиции сайта в Google для разных запросов по времени.

---

### 📄 Page Analyses
Анализ отдельных страниц сайта.

```sql
CREATE TABLE page_analyses (
    id SERIAL PRIMARY KEY,
    analysis_run_id INTEGER REFERENCES analysis_runs(id) ON DELETE CASCADE,
    
    url VARCHAR(1000) NOT NULL,
    title VARCHAR(500),
    
    word_count INTEGER DEFAULT 0,
    main_text_length INTEGER DEFAULT 0,
    keywords_found INTEGER DEFAULT 0,
    
    main_content TEXT,
    meta_description TEXT,
    meta_keywords TEXT[],
    h1_tags TEXT[],
    h2_tags TEXT[],
    
    fetch_success BOOLEAN DEFAULT true,
    error_message TEXT,
    
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON page_analyses(analysis_run_id, url);
CREATE INDEX ON page_analyses(url);
```

**Назначение:** Хранит результаты анализа каждой страницы сайта.

---

## 🔗 Связи между таблицами

```
websites (1) ──< (N) analysis_runs
                      │
                      ├──< (N) keywords ──> (1) keyword_clusters
                      │
                      └──< (N) page_analyses

websites (1) ──< (N) serp_positions ──> (1) serp_results
```

---

## 🚀 Использование

### Быстрый старт

```bash
# Запустить базу данных
./scripts/start-db.sh

# Применить миграции
./scripts/migrate.sh
```

### Примеры запросов

#### Получить все сайты

```sql
SELECT * FROM websites WHERE is_active = true;
```

#### Последние анализы для сайта

```sql
SELECT 
    ar.id,
    ar.status,
    ar.total_keywords,
    ar.total_clusters,
    ar.started_at,
    ar.completed_at
FROM analysis_runs ar
WHERE ar.website_id = 1
ORDER BY ar.started_at DESC
LIMIT 10;
```

#### Top-10 ключевых слов по TF-IDF

```sql
SELECT 
    keyword,
    intent,
    tf_idf_score,
    frequency
FROM keywords
WHERE analysis_run_id = 1
ORDER BY tf_idf_score DESC
LIMIT 10;
```

#### Распределение интентов в кластере

```sql
SELECT 
    kc.cluster_label,
    kc.cluster_name,
    kc.intent_distribution,
    kc.size
FROM keyword_clusters kc
WHERE kc.analysis_run_id = 1
ORDER BY kc.size DESC;
```

#### Динамика позиций сайта

```sql
SELECT 
    sr.query,
    sp.position,
    sp.checked_at
FROM serp_positions sp
JOIN serp_results sr ON sp.serp_result_id = sr.id
WHERE sp.website_id = 1
ORDER BY sp.checked_at DESC;
```

---

## 🔐 Безопасность

### Подключение к БД

```python
from db.manager import DatabaseManager

# Автоматически читает переменные окружения
db = DatabaseManager()

# Или явное указание
db = DatabaseManager(
    database_url="postgresql://user:pass@localhost:5434/dbname"
)
```

### Переменные окружения

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5434
export POSTGRES_DB=seo_agent
export POSTGRES_USER=seo_user
export POSTGRES_PASSWORD=seo_password
```

---

## 📚 Дополнительно

- [Управление БД через скрипты](scripts/README.md)
- [SQLAlchemy Models](models.py)
- [Database Manager](manager.py)
- [Alembic Migrations](migrations/)
