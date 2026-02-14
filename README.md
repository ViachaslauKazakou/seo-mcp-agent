# SEO MCP Agent

**Автономный SEO-агент для анализа ключевых слов, определения интента и рекомендаций по оптимизации.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://ViachaslauKazakou.github.io/seo-mcp-agent/)

---

## 📚 Документация

Полная документация доступна по адресу: **[https://ViachaslauKazakou.github.io/seo-mcp-agent/](https://ViachaslauKazakou.github.io/seo-mcp-agent/)**

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

## ⚡ Быстрый старт

### Установка

```bash
# Клонируйте репозиторий
git clone https://github.com/ViachaslauKazakou/seo-mcp-agent.git
cd seo-mcp-agent

# Установите зависимости через Poetry
poetry install

# Установите Playwright браузеры
poetry run playwright install chromium
```

### Запуск Web интерфейса

```bash
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8030 --reload
```

Откройте http://localhost:8030 в браузере.

### Запуск Desktop приложения

```bash
poetry run python desktop/main.py
```

---

## 📖 Дополнительная информация

- 📘 [Полная документация](https://ViachaslauKazakou.github.io/seo-mcp-agent/)
- 🚀 [Getting Started](https://ViachaslauKazakou.github.io/seo-mcp-agent/getting-started.html)
- 📖 [User Guide](https://ViachaslauKazakou.github.io/seo-mcp-agent/user-guide.html)
- 🔧 [Development](https://ViachaslauKazakou.github.io/seo-mcp-agent/development.html)
- 📝 [API Reference](https://ViachaslauKazakou.github.io/seo-mcp-agent/api-reference.html)

---

## 🤝 Contributing

Contributions are welcome! Please read the [Contributing Guide](https://ViachaslauKazakou.github.io/seo-mcp-agent/contributing.html).

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

- **GitHub Issues:** [github.com/ViachaslauKazakou/seo-mcp-agent/issues](https://github.com/ViachaslauKazakou/seo-mcp-agent/issues)
- **Email:** sly.kazakoff@gmail.com


