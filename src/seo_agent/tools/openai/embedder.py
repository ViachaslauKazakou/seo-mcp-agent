"""OpenAI-based embeddings tool."""

import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI

from seo_agent.models import KeywordCandidate, EmbeddingRecord


# Load environment variables
root_dir = Path(__file__).resolve().parents[4]
load_dotenv(root_dir / ".env")


class OpenAIEmbedder:
    """Generate embeddings using OpenAI API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    @property
    def is_enabled(self) -> bool:
        return self.client is not None

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts using OpenAI."""
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        response = await self.client.embeddings.create(
            model=self.model,
            input=texts
        )

        # Sort by index to ensure correct order
        embeddings = sorted(response.data, key=lambda x: x.index)
        return [emb.embedding for emb in embeddings]

    async def embed_keywords(self, keywords: List[KeywordCandidate]) -> List[EmbeddingRecord]:
        """Generate embeddings for keyword candidates."""
        if not keywords:
            return []

        keyword_texts = [kw.keyword for kw in keywords]
        embeddings = await self.embed(keyword_texts)

        records = []
        for kw, emb in zip(keywords, embeddings):
            # Use first source URL or placeholder
            source_url = kw.source_urls[0] if kw.source_urls else "unknown"
            records.append(EmbeddingRecord(
                text=kw.keyword,
                embedding=emb,
                source_url=source_url
            ))

        return records
