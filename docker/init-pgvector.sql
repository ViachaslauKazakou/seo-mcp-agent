-- Initialize pgvector extension for PostgreSQL
-- This script is automatically run by docker-entrypoint-initdb.d

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Grant usage to database user
GRANT ALL ON SCHEMA public TO seo_user;
