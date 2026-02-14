# SEO MCP Agent

![SEO Agent Logo](logo.svg)

**Автономный SEO-агент для анализа ключевых слов, определения интента и рекомендаций по оптимизации.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---
:::{grid-item-card} 🏁 Current status
:link: semantic-analyze-status
:link-type: doc

---


## 🚀 Возможности

- **Извлечение ключевых слов** через TF-IDF и embeddings
- **Определение интента** (informational, navigational, commercial, transactional)
- **Semantic clustering** ключевых слов с использованием ML
- **Анализ SERP** и конкурентов
- **Web и Desktop интерфейсы**
- **Интеграция с PlayWright** для JavaScript-heavy сайтов
- **Поддержка HuggingFace и OpenAI** embeddings

---

## 📚 Разделы документации

::::{grid} 2
:gutter: 3

:::{grid-item-card} 🏁 Getting Started
:link: getting-started
:link-type: doc

Установка, быстрый старт и настройка проекта
:::

:::{grid-item-card} 📖 User Guide
:link: user-guide
:link-type: doc

Руководство по использованию Web UI, Desktop App и CLI
:::

:::{grid-item-card} ⚡ Features
:link: features
:link-type: doc

Детальное описание функционала и возможностей
:::

:::{grid-item-card} 🔧 Development
:link: development
:link-type: doc

Архитектура, API docs и contribution guide
:::

::::

---

## 🎯 Быстрый пример

```python
from seo_agent.tools.hf.keywords import KeywordExtractor
from seo_agent.models import ParsedDocument

# Создаем экстрактор
extractor = KeywordExtractor(max_keywords=20)

# Анализируем документ
doc = ParsedDocument(
    url="https://example.com",
    title="Example Page",
    main_text="Your page content here...",
    word_count=100
)

# Извлекаем ключевые слова
keywords = extractor.extract([doc])

for kw in keywords[:5]:
    print(f"{kw.keyword}: {kw.tf_idf_score:.3f} ({kw.intent})")
```

---

## 💡 Основные концепции

### Keyword Extraction
Использует TF-IDF для извлечения наиболее значимых слов и фраз из контента сайта.

### Intent Detection
Классифицирует запросы по 4 типам интента на основе конфигурируемых правил и ML-моделей.

### Semantic Clustering
Группирует семантически связанные ключевые слова используя embeddings (HuggingFace или OpenAI).

---

## 🌟 Next Steps

```{tableofcontents}
```

---

## 📞 Поддержка

- **GitHub Issues:** [github.com/yourusername/seo-mcp-agent/issues](https://github.com/yourusername/seo-mcp-agent/issues)
- **Email:** sly.kazakoff@gmail.com
- **Documentation:** [seo-mcp-agent.readthedocs.io](https://seo-mcp-agent.readthedocs.io)

---

Built with ❤️ using [Jupyter Book](https://jupyterbook.org)
