# Installation

## Установка через Poetry (рекомендуется)

```bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/seo-mcp-agent.git
cd seo-mcp-agent

# Установите зависимости
poetry install

# Активируйте виртуальное окружение
poetry shell

# Установите Playwright browsers
poetry run playwright install
```

## Установка через pip

```bash
pip install seo-agent

# Установите Playwright browsers
playwright install
```

## Desktop приложение

Для использования десктоп версии установите дополнительные зависимости:

```bash
poetry install --extras desktop
# или
pip install seo-agent[desktop]
```

## Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
# HuggingFace (опционально, для приватных моделей)
HF_TOKEN=your_huggingface_token
HF_EMBEDDING_MODEL=all-MiniLM-L6-v2

# OpenAI (для AI-powered рекомендаций)
OPENAI_API_KEY=your_openai_key

# Яндекс.Вордстат (для будущей интеграции)
YANDEX_WORDSTAT_TOKEN=your_token
```

## Проверка установки

```bash
# Запустите тесты
poetry run pytest

# Запустите Web UI
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8030 --reload

# Откройте http://localhost:8030 в браузере
```

## Troubleshooting

### macOS ARM (M1/M2/M3)

Если возникают проблемы с зависимостями:

```bash
# Используйте Rosetta для совместимости
arch -x86_64 poetry install
```

### Torch загружается слишком долго

```bash
# Увеличьте timeout
export PIP_DEFAULT_TIMEOUT=300
poetry install
```

### Playwright браузеры

Если браузеры не установились автоматически:

```bash
poetry run python -m playwright install chromium
```

Далее: [Quick Start](quick-start.md) →