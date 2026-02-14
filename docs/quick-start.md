# Quick Start

## Web Interface

1. **Запустите сервер:**

```bash
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8030 --reload
```

2. **Откройте браузер:**

Перейдите на [http://localhost:8030](http://localhost:8030)

3. **Проанализируйте сайт:**

- Введите URL (например, `https://example.com`)
- Выберите тип парсера (Standard или PlayWright)
- Выберите embedding provider (HuggingFace или OpenAI)
- Нажмите "Analyze"

## Desktop Application

```bash
poetry run python desktop/main.py
```

Интерфейс идентичен веб-версии, но работает локально без сервера.

## CLI Usage

```bash
# Базовый анализ
seo-agent analyze https://example.com

# С дополнительными опциями
seo-agent analyze https://example.com \
  --max-keywords 30 \
  --fetcher playwright \
  --use-openai
```

## Programmatic Usage

```python
from seo_agent.tools.hf.keywords import KeywordExtractor
from seo_agent.tools.hf.clustering import Embedder, SemanticClusterer
from seo_agent.tools.hf.fetcher import HTTPXFetcher
from seo_agent.models import ParsedDocument
import asyncio

async def analyze_url(url: str):
    # 1. Fetch content
    fetcher = HTTPXFetcher()
    fetch_result = await fetcher.fetch(url)
    
    # 2. Parse to document
    doc = ParsedDocument(
        url=url,
        title="Page Title",
        main_text=fetch_result.content[:5000],  # First 5000 chars
        word_count=len(fetch_result.content.split())
    )
    
    # 3. Extract keywords
    extractor = KeywordExtractor(max_keywords=20)
    keywords = extractor.extract([doc])
    
    # 4. Create embeddings
    embedder = Embedder()
    embeddings = embedder.embed_keywords(keywords)
    
    # 5. Cluster keywords
    clusterer = SemanticClusterer(n_clusters=3)
    clusters = clusterer.cluster(keywords, embeddings)
    
    # 6. Print results
    print(f"\n🔑 Top Keywords:")
    for kw in keywords[:10]:
        print(f"  {kw.keyword:30} | TF-IDF: {kw.tf_idf_score:.3f} | Intent: {kw.intent}")
    
    print(f"\n📊 Clusters:")
    for cluster in clusters:
        print(f"  Cluster {cluster.cluster_id}: {cluster.topic_summary}")
        print(f"    Size: {cluster.size}, Cohesion: {cluster.cohesion_score:.3f}")

# Run
asyncio.run(analyze_url("https://example.com"))
```

## Результаты анализа

После анализа вы получите:

- **Keywords Extracted:** Список ключевых слов с TF-IDF scores и интентом
- **Intent Breakdown:** Распределение по типам интента
- **Clusters:** Семантические группы ключевых слов
- **Recommendations:** AI-powered рекомендации (если включен OpenAI)

## Следующие шаги

- [Configuration](configuration.md) - Настройте конфигурацию
- [Web Interface](web-interface.md) - Детальное описание веб-интерфейса
- [Features](features.md) - Узнайте о всех возможностях