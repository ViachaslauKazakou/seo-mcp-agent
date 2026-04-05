#!/bin/bash
# Connect to PostgreSQL CLI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${COMPOSE_FILE:-containers/docker-compose.dev.yml}"
DOCKER_COMPOSE=(docker-compose -f "$COMPOSE_FILE")

cd "$PROJECT_ROOT"

echo "🔗 Connecting to PostgreSQL CLI..."
echo ""

"${DOCKER_COMPOSE[@]}" exec postgres psql -U seo_user -d seo_agent
