-- Additional PostgreSQL extensions for SEO Agent

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable full-text search support
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Enable unaccent for text normalization
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Verify installations
SELECT extname, extversion 
FROM pg_extension 
WHERE extname IN ('uuid-ossp', 'pg_trgm', 'unaccent')
ORDER BY extname;

COMMENT ON EXTENSION vector IS 'pgvector extension for vector similarity search';
COMMENT ON EXTENSION "uuid-ossp" IS 'Generate UUIDs';
COMMENT ON EXTENSION "pg_trgm" IS 'Trigram similarity for text search';
COMMENT ON EXTENSION "unaccent" IS 'Remove accents from text';
