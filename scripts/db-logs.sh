#!/bin/bash
# View database logs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "📋 PostgreSQL logs (Ctrl+C to exit):"
echo ""

docker-compose logs -f postgres
