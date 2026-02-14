# Configuration

## Environment Variables

Создайте файл `.env` в корневой директории проекта:

```bash
# HuggingFace Configuration
HF_TOKEN=your_huggingface_token              # Опционально для приватных моделей
HF_EMBEDDING_MODEL=all-MiniLM-L6-v2          # Default embedding model

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key           # Для AI-powered рекомендаций
OPENAI_MODEL=gpt-4o-mini                     # Default chat model
OPENAI_EMBEDDING_MODEL=text-embedding-3-small # Default embedding model

# Yandex.Wordstat (Future)
YANDEX_WORDSTAT_TOKEN=your_token

# Server Configuration
HOST=0.0.0.0
PORT=8030
```

## Keyword Extraction Settings

### Stop Words

Редактируйте `src/seo_agent/tools/hf/stopwords.py`:

```python
# Добавьте свои стоп-слова
CUSTOM_STOPWORDS = {
    "ваше", "слово", "здесь"
}

ALL_STOPWORDS = RUSSIAN_STOPWORDS | ENGLISH_STOPWORDS | CUSTOM_STOPWORDS
```

### Intent Detection Rules

Настройте правила в `src/seo_agent/tools/hf/config.py`:

```python
# Добавьте свои фразы для каждого типа интента
TRANSACTIONAL_PHRASES = [
    "купить", "заказать", "цена", "стоимость",
    # Ваши дополнительные фразы
    "оформить заказ", "добавить в корзину"
]
```

## Clustering Parameters

```python
from seo_agent.tools.hf.clustering import SemanticClusterer

# Измените количество кластеров
clusterer = SemanticClusterer(
    n_clusters=5,        # Количество кластеров
    random_state=42      # Seed для воспроизводимости
)
```

## Fetcher Configuration

### HTTP Fetcher

```python
from seo_agent.tools.hf.fetcher import HTTPXFetcher

fetcher = HTTPXFetcher(
    timeout=30000,       # Timeout в миллисекундах
    follow_redirects=True
)
```

### PlayWright Fetcher (для JS-heavy сайтов)

```python
from seo_agent.tools.hf.fetcher import PlayWrightFetcher

fetcher = PlayWrightFetcher(
    timeout=60000,       # Timeout в миллисекундах
    headless=False,      # False для обхода детекторов ботов
    stealth_mode=True    # Включить stealth режим
)
```

## Logging Configuration

Создайте `logging.conf`:

```ini
[loggers]
keys=root,seo_agent

[handlers]
keys=console,file

[formatters]
keys=detailed

[logger_root]
level=INFO
handlers=console

[logger_seo_agent]
level=DEBUG
handlers=console,file
qualname=seo_agent
propagate=0

[handler_console]
class=StreamHandler
level=INFO
formatter=detailed
args=(sys.stdout,)

[handler_file]
class=FileHandler
level=DEBUG
formatter=detailed
args=('seo_agent.log', 'a')

[formatter_detailed]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S
```

Используйте в коде:

```python
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('seo_agent')
```

## Database Configuration (Future)

```python
# src/seo_agent/db/config.py
DATABASE_URL = "sqlite:///./seo_agent.db"
# или PostgreSQL:
# DATABASE_URL = "postgresql://user:password@localhost/seo_agent"
```

## Advanced Settings

### TF-IDF Parameters

```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    ngram_range=(1, 3),    # uni/bi/trigrams
    max_features=100,       # Максимум фич
    stop_words='english',   # Встроенные стоп-слова
    min_df=1,              # Минимальная частота документа
    max_df=0.8             # Максимальная частота (исключить слишком частые)
)
```

### Embedding Models

#### HuggingFace Models

```python
# Быстрая, но менее точная
"all-MiniLM-L6-v2"           # 384 dims, 80MB

# Более точная, но медленнее
"all-mpnet-base-v2"          # 768 dims, 420MB

# Для мультиязычности
"paraphrase-multilingual-MiniLM-L12-v2"  # 384 dims
```

#### OpenAI Models

```python
"text-embedding-3-small"     # 1536 dims, дешевле
"text-embedding-3-large"     # 3072 dims, точнее
```

## Next Steps

- [Web Interface](web-interface.md) - Использование веб-интерфейса
- [API Reference](api-reference.md) - Документация API
