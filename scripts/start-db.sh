#!/bin/bash
# Start PostgreSQL database using Docker Compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting PostgreSQL database..."

cd "$PROJECT_ROOT"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start PostgreSQL container
docker-compose up -d postgres

# Wait for PostgreSQL to be healthy
echo "⏳ Waiting for PostgreSQL to be healthy..."
timeout 60 bash -c 'until docker-compose exec -T postgres pg_isready -U seo_user -d seo_agent > /dev/null 2>&1; do sleep 1; done'

if [ $? -eq 0 ]; then
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
    echo "💡 To stop: docker-compose down"
    echo "💡 To view logs: docker-compose logs -f postgres"
else
    echo "❌ Failed to start PostgreSQL within 60 seconds"
    docker-compose logs postgres
    exit 1
fi
