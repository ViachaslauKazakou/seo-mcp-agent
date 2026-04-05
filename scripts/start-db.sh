#!/bin/bash
# Start PostgreSQL database using Docker Compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${COMPOSE_FILE:-containers/docker-compose.dev.yml}"
DOCKER_COMPOSE=(docker-compose -f "$COMPOSE_FILE")

echo "🚀 Starting PostgreSQL database..."

cd "$PROJECT_ROOT"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start PostgreSQL container
"${DOCKER_COMPOSE[@]}" up -d postgres

# Wait for PostgreSQL to be healthy
echo "⏳ Waiting for PostgreSQL to be healthy..."
MAX_WAIT_SECONDS=60
START_TIME=$(date +%s)
until "${DOCKER_COMPOSE[@]}" exec -T postgres pg_isready -U seo_user -d seo_agent > /dev/null 2>&1; do
    NOW=$(date +%s)
    if [ $((NOW - START_TIME)) -ge "$MAX_WAIT_SECONDS" ]; then
        echo "❌ Failed to start PostgreSQL within ${MAX_WAIT_SECONDS} seconds"
        "${DOCKER_COMPOSE[@]}" logs postgres
        exit 1
    fi
    sleep 1
done

if "${DOCKER_COMPOSE[@]}" exec -T postgres pg_isready -U seo_user -d seo_agent > /dev/null 2>&1; then
    echo "✅ PostgreSQL is up and running!"
    echo ""
    echo "📊 Database connection info:"
    echo "   Host: localhost"
    echo "   Port: 5434"
    echo "   Database: seo_agent"
    echo "   User: seo_user"
    echo "   Password: seo_password"
    echo ""
    echo "🔗 Connection string:"
    echo "   postgresql://seo_user:seo_password@localhost:5434/seo_agent"
    echo ""
    echo "💡 To stop: docker-compose -f $COMPOSE_FILE down"
    echo "💡 To view logs: docker-compose -f $COMPOSE_FILE logs -f postgres"
else
    echo "❌ Failed to verify PostgreSQL health"
    "${DOCKER_COMPOSE[@]}" logs postgres
    exit 1
fi
