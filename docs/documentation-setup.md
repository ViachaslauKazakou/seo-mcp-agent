# Настройка и разворачивание документации

Документация SEO MCP Agent построена на базе [Sphinx](https://www.sphinx-doc.org/) с использованием темы [Sphinx Book Theme](https://sphinx-book-theme.readthedocs.io/) и расширения [MyST Parser](https://myst-parser.readthedocs.io/) для поддержки Markdown.

---

## 📦 Установка зависимостей

Все зависимости для документации уже включены в проект и устанавливаются автоматически:

```bash
poetry install
```

Основные пакеты для документации:

- **sphinx** ≥9.0.0 — генератор документации
- **sphinx-book-theme** ≥1.1.0 — тема оформления
- **myst-parser** ≥5.0.0 — поддержка Markdown
- **sphinx-design** — компоненты UI (карточки, grid)
- **sphinx-autodoc-typehints** — автодокументация с типами
- **sphinx-autobuild** — live-reload сервер (dev)

---

## 🚀 Локальный запуск

### Быстрая сборка

Собрать HTML-документацию единожды:

```bash
poetry run sphinx-build -b html docs docs/_build/html
```

Открыть в браузере:

```bash
open docs/_build/html/index.html  # macOS
xdg-open docs/_build/html/index.html  # Linux
start docs/_build/html/index.html  # Windows
```

### Live-reload сервер

Запустить сервер с автоматической пересборкой при изменениях:

```bash
poetry run sphinx-autobuild docs docs/_build/html --port 8080
```

Документация будет доступна по адресу: **http://localhost:8080**

Сервер автоматически отслеживает изменения в:
- Markdown файлах (`.md`)
- Конфигурации (`conf.py`)
- Шаблонах

Для остановки нажмите `Ctrl+C`.

---

## 📁 Структура документации

```
docs/
├── conf.py                      # Конфигурация Sphinx
├── index.md                     # Главная страница
├── getting-started.md           # Начало работы
├── installation.md              # Установка
├── quick-start.md               # Быстрый старт
├── user-guide.md                # Руководство пользователя
├── features.md                  # Возможности
├── configuration.md             # Настройка
├── keyword-extraction.md        # Извлечение ключевых слов
├── intent-detection.md          # Определение интента
├── clustering.md                # Кластеризация
├── serp-analysis.md             # SERP анализ
├── web-interface.md             # Web-интерфейс
├── desktop-app.md               # Desktop приложение
├── cli-usage.md                 # CLI использование
├── development.md               # Разработка
├── architecture.md              # Архитектура
├── api-reference.md             # API референс
├── contributing.md              # Вклад в проект
├── testing.md                   # Тестирование
├── examples/                    # Примеры использования
│   ├── basic-analysis.md
│   ├── advanced-clustering.md
│   └── custom-integration.md
└── _build/                      # Собранная документация (git ignore)
    └── html/
```

---

## ⚙️ Конфигурация (conf.py)

Основные настройки документации находятся в [docs/conf.py](conf.py):

```python
# Информация о проекте
project = 'SEO MCP Agent'
copyright = '2026, Viachaslau Kazakou'
author = 'Viachaslau Kazakou'
release = '0.1.0'

# Расширения Sphinx
extensions = [
    'sphinx.ext.autodoc',           # Автодокументация из docstrings
    'sphinx.ext.napoleon',          # Поддержка Google/NumPy стиля
    'sphinx.ext.viewcode',          # Ссылки на исходный код
    'sphinx.ext.intersphinx',       # Ссылки на другие проекты
    'myst_parser',                  # Поддержка Markdown
    'sphinx_autodoc_typehints',     # Типы в документации
    'sphinx_design',                # UI компоненты
]

# MyST расширения
myst_enable_extensions = [
    "colon_fence",    # ::: синтаксис для директив
    "deflist",        # Списки определений
    "tasklist",       # Чекбоксы
]

# Тема оформления
html_theme = 'sphinx_book_theme'
```

---

## 📝 Синтаксис MyST Markdown

MyST расширяет стандартный Markdown для Sphinx:

### Директивы с :::

```markdown
:::{note}
Это заметка в красивом блоке
:::

:::{warning}
Предупреждение!
:::

:::{tip}
Полезный совет
:::
```

### Grid карточки

```markdown
::::{grid} 2
:gutter: 3

:::{grid-item-card} Заголовок 1
:link: page1
:link-type: doc

Описание карточки
:::

:::{grid-item-card} Заголовок 2
:link: page2
:link-type: doc

Описание карточки
:::

::::
```

### Toctree (навигация)

```markdown
\```{toctree}
:maxdepth: 2
:caption: Раздел

page1
page2
page3
\```
```

### Ссылки на документы

```markdown
[Текст ссылки](another-page)
[Текст ссылки](another-page.md)
{doc}`another-page`
```

---

## 🌐 GitHub Pages деплой

Документация автоматически публикуется на GitHub Pages при пуше в ветку `main`.

### Workflow конфигурация

Файл [.github/workflows/docs.yml](../.github/workflows/docs.yml):

```yaml
name: Deploy Documentation

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: 1.8.0
          virtualenvs-create: true
          virtualenvs-in-project: true
      
      - name: Install dependencies
        run: poetry install --no-interaction
      
      - name: Build documentation
        run: |
          cd docs
          poetry run sphinx-build -b html . _build/html
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/_build/html

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Настройка репозитория

1. Перейдите в **Settings** → **Pages**
2. В разделе **Build and deployment** выберите:
   - **Source**: GitHub Actions
3. При следующем пуше в `main` документация соберется автоматически

Документация будет доступна по адресу:
```
https://<username>.github.io/<repository>/
```

---

## 🔧 Расширение документации

### Добавление новой страницы

1. Создайте файл `docs/new-page.md`
2. Добавьте контент в Markdown формате
3. Добавьте ссылку в `toctree` в [index.md](index.md):

```markdown
\```{toctree}
:maxdepth: 2
:caption: Раздел

existing-page
new-page
\```
```

### Автодокументация API

Для автоматической генерации документации из docstrings:

```markdown
\```{eval-rst}
.. automodule:: seo_agent.tools.keywords
   :members:
   :undoc-members:
   :show-inheritance:
\```
```

Или создайте `.rst` файл:

```rst
API Reference
=============

.. automodule:: seo_agent.tools.keywords
   :members:
   :undoc-members:
   :show-inheritance:
```

---

## 🐛 Troubleshooting

### Ошибка: "Unknown directive type"

Проверьте, что расширение добавлено в `conf.py`:

```python
extensions = [
    'sphinx_design',  # Для grid, card
    'myst_parser',    # Для Markdown
]
```

### Ошибка: "Document isn't included in any toctree"

Добавьте документ в `toctree` в `index.md` или другой главной странице.

### Стили не применяются

Очистите кеш сборки:

```bash
rm -rf docs/_build
poetry run sphinx-build -b html docs docs/_build/html
```

### GitHub Actions падает

Проверьте, что все зависимости документации есть в `pyproject.toml`:

```toml
[tool.poetry.dependencies]
sphinx = ">=9.0.0"
sphinx-book-theme = ">=1.1.0"
myst-parser = ">=5.0.0"
sphinx-design = "^0.7.0"
sphinx-autodoc-typehints = ">=3.6.0"
```

---

## 📚 Полезные ссылки

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [MyST Parser Guide](https://myst-parser.readthedocs.io/)
- [Sphinx Book Theme](https://sphinx-book-theme.readthedocs.io/)
- [Sphinx Design Components](https://sphinx-design.readthedocs.io/)
- [GitHub Pages Documentation](https://docs.github.com/pages)

---

## 💬 Поддержка

Если возникли проблемы с документацией:

1. Проверьте [Issues](https://github.com/ViachaslauKazakou/seo-mcp-agent/issues)
2. Создайте новый Issue с меткой `documentation`
3. Напишите на sly.kazakoff@gmail.com
