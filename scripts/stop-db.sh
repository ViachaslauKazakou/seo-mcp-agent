#!/bin/bash
# Stop PostgreSQL database

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🛑 Stopping PostgreSQL database..."

cd "$PROJECT_ROOT"

docker-compose down

echo "✅ PostgreSQL stopped"
echo ""
echo "💡 Data is preserved in Docker volume: seo-mcp-agent_postgres_data"
echo "💡 To completely remove data: docker-compose down -v"
