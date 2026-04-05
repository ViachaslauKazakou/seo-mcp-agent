#!/bin/bash
# View database logs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${COMPOSE_FILE:-containers/docker-compose.dev.yml}"
DOCKER_COMPOSE=(docker-compose -f "$COMPOSE_FILE")

cd "$PROJECT_ROOT"

echo "📋 PostgreSQL logs (Ctrl+C to exit):"
echo ""

"${DOCKER_COMPOSE[@]}" logs -f postgres
