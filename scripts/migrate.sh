#!/bin/bash
# Run database migrations using Alembic

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔄 Running database migrations..."

# Set environment variables for database connection
export POSTGRES_HOST=${POSTGRES_HOST:-localhost}
export POSTGRES_PORT=${POSTGRES_PORT:-5434}
export POSTGRES_DB=${POSTGRES_DB:-seo_agent}
export POSTGRES_USER=${POSTGRES_USER:-seo_user}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-seo_password}

cd "$PROJECT_ROOT"

# Check if database is accessible
echo "📡 Checking database connection..."
if ! docker-compose exec -T postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; then
    echo "❌ Database is not accessible. Please run ./scripts/start-db.sh first."
    exit 1
fi

echo "✅ Database connection OK"

# Run migrations
cd "$PROJECT_ROOT/src/db"

echo "📋 Current migration status:"
poetry run alembic -c alembic.ini current

echo ""
echo "⬆️  Applying migrations to head..."
poetry run alembic -c alembic.ini upgrade head

echo ""
echo "✅ Migrations completed!"
echo ""
echo "📊 Current schema version:"
poetry run alembic -c alembic.ini current
