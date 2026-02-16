# Makefile Documentation

Makefile для автоматизации частых задач в проекте SEO MCP Agent.

## 📋 Быстрый старт

```bash
# Показать все доступные команды
make help

# Полная установка проекта
make setup

# Запустить приложение
make dev
```

---

## 📚 Категории команд

### 🔧 Installation & Setup

#### `make install`
Устанавливает все зависимости проекта через Poetry и Playwright.

```bash
make install
```

#### `make update`
Обновляет все зависимости до последних версий.

```bash
make update
```

#### `make clean`
Удаляет кеш файлы и временные директории.

```bash
make clean
```

---

### 💾 Database Management

#### `make db-start`
Запускает PostgreSQL через Docker Compose.

```bash
make db-start
```

**Эквивалент:** `./scripts/start-db.sh`

#### `make db-stop`
Останавливает PostgreSQL контейнер.

```bash
make db-stop
```

#### `make db-migrate`
Применяет все pending миграции к базе данных.

```bash
make db-migrate
```

#### `make db-create-migration MSG="message"`
Создаёт новую миграцию с автогенерацией.

```bash
make db-create-migration MSG="Add user preferences table"
```

**Обязательный параметр:** `MSG` - описание миграции

#### `make db-init`
Инициализирует базу данных (создаёт таблицы без миграций).

```bash
make db-init
```

#### `make db-reset`
⚠️ **ОПАСНО:** Удаляет все данные и пересоздаёт схему.

```bash
make db-reset
```

#### `make db-shell`
Открывает PostgreSQL CLI (psql).

```bash
make db-shell
```

#### `make db-logs`
Показывает логи PostgreSQL в реальном времени.

```bash
make db-logs
```

#### `make db-status`
Проверяет статус контейнера PostgreSQL.

```bash
make db-status
```

---

### 🚀 Application

#### `make run-web`
Запускает FastAPI веб-приложение с hot-reload.

```bash
make run-web
```

**URL:** http://localhost:8030

#### `make run-desktop`
Запускает PySide6 desktop приложение.

```bash
make run-desktop
```

#### `make dev`
Запускает БД и веб-приложение (dev режим).

```bash
make dev
```

---

### 🧪 Testing & Quality

#### `make test`
Запускает тесты с pytest.

```bash
make test
```

#### `make test-cov`
Запускает тесты с отчётом о покрытии кода.

```bash
make test-cov
```

**Генерирует:** `htmlcov/index.html`

#### `make lint`
Проверяет код с flake8.

```bash
make lint
```

#### `make format`
Форматирует код с black.

```bash
make format
```

#### `make format-check`
Проверяет форматирование без изменений.

```bash
make format-check
```

#### `make typecheck`
Проверяет типы с mypy.

```bash
make typecheck
```

#### `make quality`
Запускает все проверки качества (format + lint + typecheck).

```bash
make quality
```

---

### 📚 Documentation

#### `make docs`
Собирает HTML документацию с Sphinx.

```bash
make docs
```

**Результат:** `docs/_build/html/index.html`

#### `make docs-open`
Собирает документацию и открывает в браузере.

```bash
make docs-open
```

#### `make docs-live`
Запускает live-reload сервер документации.

```bash
make docs-live
```

**URL:** http://localhost:8080

#### `make docs-clean`
Удаляет build документации.

```bash
make docs-clean
```

---

### 🐳 Docker

#### `make docker-up`
Запускает все Docker сервисы.

```bash
make docker-up
```

#### `make docker-down`
Останавливает все Docker сервисы.

```bash
make docker-down
```

#### `make docker-build`
Собирает Docker образы.

```bash
make docker-build
```

#### `make docker-logs`
Показывает логи всех контейнеров.

```bash
make docker-logs
```

#### `make docker-ps`
Показывает статус контейнеров.

```bash
make docker-ps
```

#### `make docker-clean`
Удаляет все контейнеры и volumes.

```bash
make docker-clean
```

---

### ⚙️ Project Setup

#### `make setup`
Полная установка проекта: install + db-start + db-migrate.

```bash
make setup
```

**Выполняет:**
1. `poetry install`
2. `playwright install chromium`
3. `./scripts/start-db.sh`
4. `./scripts/migrate.sh`

#### `make env-example`
Создаёт `.env` из `.env.example`.

```bash
make env-example
```

#### `make check-env`
Проверяет наличие `.env` файла.

```bash
make check-env
```

---

### 🔄 CI/CD

#### `make ci-test`
Запускает тесты для CI (с coverage XML).

```bash
make ci-test
```

#### `make ci-lint`
Проверяет код для CI.

```bash
make ci-lint
```

#### `make ci-docs`
Собирает документацию для CI (с warnings as errors).

```bash
make ci-docs
```

#### `make ci`
Запускает все CI проверки.

```bash
make ci
```

---

### 🛠️ Utilities

#### `make version`
Показывает версию проекта.

```bash
make version
```

#### `make shell`
Открывает Poetry shell.

```bash
make shell
```

#### `make info`
Показывает информацию о проекте.

```bash
make info
```

#### `make scripts-help`
Показывает справку по bash-скриптам БД.

```bash
make scripts-help
```

---

### ⚡ Quick Commands

#### `make quick-start`
Быстрый старт: setup + run-web.

```bash
make quick-start
```

#### `make quick-test`
Быстрый тест: lint + test.

```bash
make quick-test
```

#### `make quick-fix`
Быстрое исправление: format + lint.

```bash
make quick-fix
```

---

## 🎯 Типичные сценарии

### Первый запуск проекта

```bash
# 1. Клонировать репозиторий
git clone https://github.com/ViachaslauKazakou/seo-mcp-agent.git
cd seo-mcp-agent

# 2. Полная установка
make setup

# 3. Создать .env
make env-example
# Отредактировать .env

# 4. Запустить приложение
make run-web
```

### Ежедневная разработка

```bash
# Утро: запустить dev окружение
make dev

# Работа с кодом...

# Перед коммитом
make quick-fix
make test

# Вечер: остановить БД
make db-stop
```

### Изменение схемы БД

```bash
# 1. Изменить models.py
vim src/db/models.py

# 2. Создать миграцию
make db-create-migration MSG="Add new column"

# 3. Применить миграцию
make db-migrate

# 4. Проверить
make db-shell
# \d table_name
```

### Подготовка к релизу

```bash
# 1. Проверить качество кода
make quality

# 2. Запустить тесты
make test-cov

# 3. Собрать документацию
make docs

# 4. Запустить CI проверки
make ci
```

### Сброс окружения

```bash
# Остановить всё
make docker-down

# Очистить кеш
make clean

# Очистить Docker (с данными)
make docker-clean

# Переустановить
make setup
```

---

## 🔧 Переменные окружения

Makefile поддерживает стандартные переменные окружения:

```bash
# Использование с custom портом
POSTGRES_PORT=5435 make db-migrate

# Использование с другой БД
POSTGRES_DB=test_db make db-start
```

---

## 📝 Добавление новых команд

Структура команды в Makefile:

```makefile
##@ Category Name

command-name: dependencies ## Command description
	@echo "$(BLUE)Message...$(NC)"
	# команды
```

**Цвета:**
- `$(BLUE)` - синий (информация)
- `$(GREEN)` - зелёный (успех)
- `$(YELLOW)` - жёлтый (предупреждение)
- `$(RED)` - красный (ошибка)
- `$(NC)` - сброс цвета

---

## 🐛 Troubleshooting

### Make команда не найдена

**macOS/Linux:**
```bash
# Проверить наличие
which make

# Установить (macOS)
xcode-select --install

# Установить (Ubuntu/Debian)
sudo apt install build-essential
```

### Ошибка "No rule to make target"

Проверьте правильность написания команды:
```bash
make help  # Показать все доступные команды
```

### Права доступа к скриптам

```bash
chmod +x scripts/*.sh
```

### Docker не запускается

```bash
# Проверить Docker
docker info

# Запустить Docker Desktop (macOS)
open -a Docker
```

---

## 📚 Ссылки

- [GNU Make Manual](https://www.gnu.org/software/make/manual/)
- [Makefile Tutorial](https://makefiletutorial.com/)
- [Scripts Documentation](scripts/README.md)
- [Database Documentation](src/db/README.md)

---

## 💡 Tips

1. **Tab completion:** Используйте `make <Tab>` для автодополнения
2. **Dry run:** `make -n command` показывает команды без выполнения
3. **Verbose:** `make command V=1` для подробного вывода
4. **Параллельно:** `make -j4` для параллельного выполнения
5. **Help всегда:** `make help` или просто `make` показывает справку
