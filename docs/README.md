# Документация SEO MCP Agent

## 📚 Как создать документацию

### Локальная сборка

```bash
# 1. Установите зависимости (если еще не установлены)
poetry install

# 2. Постройте документацию
poetry run jupyter-book build docs

# 3. Откройте результат
open docs/_build/html/index.html
```

### Публикация на GitHub Pages

Документация автоматически публикуется при push в ветку `main` через GitHub Actions.

#### Настройка GitHub Pages:

1. **Перейдите в Settings → Pages**
2. **Source:** Deploy from a branch
3. **Branch:** `gh-pages` / `root`
4. **Сохраните**

После этого документация будет доступна по адресу:
```
https://yourusername.github.io/seo-mcp-agent/
```

### Структура документации

```
docs/
├── _config.yml           # Конфигурация Jupyter Book
├── _toc.yml             # Оглавление (Table of Contents)
├── index.md             # Главная страница
├── logo.svg             # Логотип проекта
├── references.bib       # Библиография
│
├── getting-started.md   # Начало работы
├── installation.md      # Установка
├── quick-start.md       # Быстрый старт
├── configuration.md     # Конфигурация
│
├── user-guide.md        # Руководство пользователя
├── web-interface.md     # Веб-интерфейс
├── desktop-app.md       # Desktop приложение
├── cli-usage.md         # CLI
├── api-reference.md     # API справка
│
├── features.md          # Возможности
├── keyword-extraction.md
├── intent-detection.md
├── clustering.md
├── serp-analysis.md
│
├── development.md       # Разработка
├── architecture.md
├── api-docs.md
├── contributing.md
├── testing.md
│
└── examples/            # Примеры
    ├── basic-analysis.md
    ├── advanced-clustering.md
    └── custom-integration.md
```

## 🔧 Редактирование документации

### Markdown файлы

Вся документация написана в Markdown формате. Jupyter Book поддерживает:

- **MyST Markdown** (расширенный синтаксис)
- **Jupyter Notebooks** (.ipynb)
- **reStructuredText** (.rst)

### Добавление новой страницы

1. Создайте `.md` файл в `docs/`
2. Добавьте запись в `docs/_toc.yml`:

```yaml
chapters:
  - file: your-new-page
    sections:
      - file: subsection-1
      - file: subsection-2
```

3. Пересоберите документацию

### Автодокументация Python кода

Добавьте в ваш Python файл docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Краткое описание функции.

    Args:
        param1: Описание первого параметра
        param2: Описание второго параметра

    Returns:
        Описание возвращаемого значения

    Example:
        >>> my_function("test", 42)
        True
    """
    pass
```

Затем добавьте в документацию:

````markdown
```{eval-rst}
.. automodule:: seo_agent.tools.hf.keywords
   :members:
   :undoc-members:
   :show-inheritance:
```
````

## 📝 Полезные команды

```bash
# Очистить сборку
poetry run jupyter-book clean docs

# Пересобрать все
poetry run jupyter-book clean docs && poetry run jupyter-book build docs

# Проверить ссылки
poetry run jupyter-book build docs --builder linkcheck

# Собрать PDF (требуется LaTeX)
poetry run jupyter-book build docs --builder pdflatex
```

## 🎨 Кастомизация

### Темы

Редактируйте `docs/_config.yml`:

```yaml
sphinx:
  config:
    html_theme: sphinx_book_theme
    html_theme_options:
      logo_only: true
      show_toc_level: 2
```

Доступные темы:
- `sphinx_book_theme` (по умолчанию)
- `sphinx_rtd_theme`
- `pydata_sphinx_theme`

### Логотип и favicon

Замените `docs/logo.svg` своим логотипом.

## 🚀 Публикация

### GitHub Pages (рекомендуется)

GitHub Actions автоматически публикует документацию при push в `main`.

Workflow находится в `.github/workflows/docs.yml`.

### Read the Docs

1. Зарегистрируйтесь на [readthedocs.org](https://readthedocs.org)
2. Импортируйте свой GitHub репозиторий
3. RTD автоматически соберет документацию

### Netlify

1. Создайте `netlify.toml`:

```toml
[build]
  command = "pip install jupyter-book && jupyter-book build docs"
  publish = "docs/_build/html"
```

2. Подключите репозиторий к Netlify

## 📖 Полезные ссылки

- [Jupyter Book Documentation](https://jupyterbook.org)
- [MyST Markdown Syntax](https://mystmd.org/guide)
- [Sphinx Documentation](https://www.sphinx-doc.org)
- [sphinx-autodoc-typehints](https://github.com/tox-dev/sphinx-autodoc-typehints)

---

**Последнее обновление:** 14 февраля 2026
