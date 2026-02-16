#!/bin/bash
# Connect to PostgreSQL CLI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🔗 Connecting to PostgreSQL CLI..."
echo ""

docker-compose exec postgres psql -U seo_user -d seo_agent
