#!/bin/bash
# Reset database (drop all data and recreate schema)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "⚠️  WARNING: This will DELETE ALL DATA in the database!"
read -p "Are you sure? (yes/no): " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Cancelled"
    exit 0
fi

# Set environment variables
export POSTGRES_HOST=${POSTGRES_HOST:-localhost}
export POSTGRES_PORT=${POSTGRES_PORT:-5434}
export POSTGRES_DB=${POSTGRES_DB:-seo_agent}
export POSTGRES_USER=${POSTGRES_USER:-seo_user}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-seo_password}

cd "$PROJECT_ROOT"

echo "🗑️  Dropping all tables..."
cd "$PROJECT_ROOT/src/db"
poetry run alembic -c alembic.ini downgrade base

echo ""
echo "⬆️  Applying all migrations..."
poetry run alembic -c alembic.ini upgrade head

echo ""
echo "✅ Database reset complete!"
