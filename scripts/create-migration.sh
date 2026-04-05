#!/bin/bash
# Create a new database migration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${COMPOSE_FILE:-containers/docker-compose.dev.yml}"
DOCKER_COMPOSE=(docker-compose -f "$COMPOSE_FILE")

# Check if migration message is provided
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <migration_message>"
    echo "   Example: $0 'Add user table'"
    exit 1
fi

MIGRATION_MESSAGE="$1"

echo "📝 Creating new migration: $MIGRATION_MESSAGE"

# Set environment variables for database connection
export POSTGRES_HOST=${POSTGRES_HOST:-localhost}
export POSTGRES_PORT=${POSTGRES_PORT:-5434}
export POSTGRES_DB=${POSTGRES_DB:-seo_agent}
export POSTGRES_USER=${POSTGRES_USER:-seo_user}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-seo_password}

cd "$PROJECT_ROOT"

# Check if database is accessible
echo "📡 Checking database connection..."
if ! "${DOCKER_COMPOSE[@]}" exec -T postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; then
    echo "❌ Database is not accessible. Please run ./scripts/start-db.sh first."
    exit 1
fi

echo "✅ Database connection OK"

echo "🔍 Detecting schema changes..."
"${DOCKER_COMPOSE[@]}" run --rm app sh -lc "cd /app/src/db && alembic -c alembic.ini revision --autogenerate -m \"$MIGRATION_MESSAGE\""

echo ""
echo "✅ Migration created successfully!"
echo ""
echo "💡 Review the migration file in src/db/migrations/versions/"
echo "💡 Apply migration with: ./scripts/migrate.sh"
