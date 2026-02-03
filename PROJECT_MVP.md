# 🔍 SEO Agent — MVP

Autonomous SEO agent with modular pipeline, FastAPI backend, and CLI interface.

## Quick Start

### Setup

```bash
# Install dependencies
poetry install

# Install browser drivers (for Playwright)
playwright install
```

### Run Analysis (CLI)

```bash
# Analyze single URL
poetry run seo-agent analyze --url https://example.com

# Analyze multiple URLs with depth
poetry run seo-agent analyze -u https://example.com -u https://example.com/blog -d 1

# Save output to JSON
poetry run seo-agent analyze --url https://example.com --output results.json
```

### Start Web Server

```bash
poetry run seo-agent server
# Open http://127.0.0.1:8000
```

## Project Structure

```
seo-agent/
├── src/seo_agent/
│   ├── models/
│   │   └── __init__.py        # Pydantic contracts (InputSpec, Cluster, Recommendation, etc.)
│   ├── tools/
│   │   ├── fetcher.py         # Fetch & parse URLs (Playwright, trafilatura)
│   │   ├── keywords.py        # Keyword extraction (TF-IDF)
│   │   └── clustering.py      # Semantic clustering (embeddings, K-means)
│   ├── agent.py               # SEO Agent orchestrator
│   ├── api/
│   │   └── app.py             # FastAPI app + web UI
│   └── cli/
│       └── main.py            # CLI commands
├── tests/                      # Test suite
├── pyproject.toml             # Poetry config
└── README.md
```

## Architecture (Variant B)

```
CLI/API Input (InputSpec)
    ↓
Fetcher (Playwright + trafilatura)
    ↓
Parser (HTML → ParsedDocument)
    ↓
KeywordExtractor (TF-IDF → KeywordCandidate)
    ↓
Embedder (sentence-transformers)
    ↓
SemanticClusterer (K-means → Cluster)
    ↓
RecommendationEngine
    ↓
RunReport (JSON/API)
```

## Data Contracts

All data flows through **Pydantic models** (see [src/seo_agent/models/__init__.py](src/seo_agent/models/__init__.py)):

| Model | Purpose |
|-------|---------|
| `InputSpec` | Input: URLs, language, crawl settings |
| `FetchResult` | Raw HTML + headers |
| `ParsedDocument` | Cleaned text, headings, structure |
| `KeywordCandidate` | Extracted phrases with scores |
| `EmbeddingRecord` | Vector representations |
| `Cluster` | Semantic groups + topic summaries |
| `Recommendation` | SEO advice with evidence |
| `RunReport` | Final output report |

## Tech Stack

- **Language:** Python 3.11+
- **Web:** FastAPI + Uvicorn
- **Parsing:** Playwright, trafilatura, readability-lxml
- **NLP:** scikit-learn, sentence-transformers
- **Storage:** PostgreSQL / MongoDB / DynamoDB (planned)
- **Package Manager:** Poetry

## Next Steps

### Phase 1 (Current)
- ✅ Modular pipeline architecture
- ✅ Core tools (fetch, parse, keywords, clustering)
- ✅ FastAPI web UI + CLI
- ⚠️ Error handling & logging
- ⚠️ Tests

### Phase 2
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Caching layer (ETag, URL deduplication)
- [ ] Advanced crawl (BFS, depth, rate limiting)
- [ ] LLM recommendations (OpenAI)

### Phase 3
- [ ] Competitor analysis
- [ ] Content gap detection
- [ ] MCP server integration
- [ ] Async job queue

## API Examples

### Analyze (POST)
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"]}'
```

Response:
```json
{
  "run_id": "run_1704287400.12",
  "status": "completed",
  "documents_parsed": 3,
  "keywords_extracted": [
    {
      "keyword": "python seo",
      "tf_idf_score": 0.45,
      "frequency": 2,
      "intent": "informational"
    }
  ],
  "clusters": [...],
  "recommendations": [...]
}
```

## Development

### Run Tests
```bash
poetry run pytest
```

### Format Code
```bash
poetry run black src/
poetry run isort src/
```

### Type Check
```bash
poetry run mypy src/
```

## License

MIT
