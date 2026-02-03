# OpenAI Embeddings Integration

## Overview
Added support for using OpenAI as an alternative embedding provider alongside HuggingFace, allowing users to choose which embedding model to use during analysis.

## Changes Made

### 1. Data Models (`src/seo_agent/models/__init__.py`)
- Added `embedding_provider` field to `InputSpec` (enum: "hf" or "openai", default: "hf")
- Added `openai_embedding_model` field to `InputSpec` (default: "text-embedding-3-small")
- Updated example JSON schema

### 2. Agent (`src/seo_agent/api/agent.py`)
- Imported `OpenAIEmbedder` from `tools/openai/embedder.py`
- Modified embedding step to:
  - Check `input_spec.embedding_provider`
  - Initialize `OpenAIEmbedder` if provider is "openai"
  - Fall back to `Embedder` (HF) if provider is "hf"
  - Use async API for OpenAI embeddings
  - Add error handling for missing OpenAI API key

### 3. CLI (`src/seo_agent/cli/main.py`)
- Added `--embedding-provider` flag (choices: "hf", "openai"; default: "hf")
- Added `--openai-embedding-model` flag (default: "text-embedding-3-small")
- Updated status output to show selected embedding provider
- Pass both fields to `InputSpec`

### 4. Web UI (`src/seo_agent/templates/index.html`)
- Added radio button selector for embedding provider ("HuggingFace" vs "OpenAI")
- Added dropdown for OpenAI embedding model selection (appears when "OpenAI" is selected)
- Updated form submission to include:
  - `embedding_provider` (selected radio value)
  - `openai_embedding_model` (selected model)
- Updated status messages to display selected embedding provider with emoji indicators

### 5. Configuration (`.env.example`)
- Added `OPENAI_EMBEDDING_MODEL` variable with documentation
- Documented supported OpenAI embedding models (text-embedding-3-small, text-embedding-3-large)
- Updated comments with model dimension information

## Usage

### Command Line
```bash
# Use HuggingFace embeddings (default)
poetry run python -m seo_agent.cli analyze --url https://example.com

# Use OpenAI embeddings
poetry run python -m seo_agent.cli analyze --url https://example.com \
  --embedding-provider openai \
  --openai-embedding-model text-embedding-3-small
```

### Web UI
1. Select embedding provider using radio buttons (HuggingFace/OpenAI)
2. If OpenAI is selected, choose embedding model from dropdown
3. Submit analysis

### Python API
```python
from seo_agent.models import InputSpec
from seo_agent.api.agent import SEOAgent

input_spec = InputSpec(
    urls=["https://example.com"],
    embedding_provider="openai",
    openai_embedding_model="text-embedding-3-small"
)

agent = SEOAgent()
report = await agent.analyze(input_spec)
```

## Architecture

```
Embedding Pipeline Selection:
  ├── HuggingFace (default)
  │   ├── Model: all-MiniLM-L6-v2 (configurable)
  │   ├── Token: Optional HF_TOKEN from .env
  │   └── Sync API (tools/hf/clustering.py)
  │
  └── OpenAI
      ├── Model: text-embedding-3-small/large (configurable)
      ├── API Key: Required OPENAI_API_KEY from .env
      └── Async API (tools/openai/embedder.py)
```

## Breaking Changes
- None. The feature is backward compatible with default "hf" provider.

## Dependencies
- No new dependencies required (openai package already in use for recommendations)

## Testing
- All Python files pass syntax validation
- Web UI supports both provider selections
- CLI accepts new flags with proper defaults
- Agent conditionally initializes correct embedder
