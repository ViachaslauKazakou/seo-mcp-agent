#!/bin/bash
# Stop PostgreSQL database

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${COMPOSE_FILE:-containers/docker-compose.dev.yml}"
DOCKER_COMPOSE=(docker-compose -f "$COMPOSE_FILE")

echo "🛑 Stopping PostgreSQL database..."

cd "$PROJECT_ROOT"

"${DOCKER_COMPOSE[@]}" down

echo "✅ PostgreSQL stopped"
echo ""
echo "💡 Data is preserved in Docker volume: containers_postgres_data"
echo "💡 To completely remove data: docker-compose -f $COMPOSE_FILE down -v"
