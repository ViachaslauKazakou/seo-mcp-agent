"""OpenAI-based recommendations tool."""

import json
import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI

from seo_agent.models import ParsedDocument, KeywordCandidate, Cluster, Recommendation


class OpenAIRecommender:
    """Generate SEO recommendations using OpenAI."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        root_dir = Path(__file__).resolve().parents[4]
        load_dotenv(root_dir / ".env")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    @property
    def is_enabled(self) -> bool:
        return self.client is not None

    async def generate_recommendations(
        self,
        documents: List[ParsedDocument],
        keywords: List[KeywordCandidate],
        clusters: List[Cluster],
        max_items: int = 5,
    ) -> List[Recommendation]:
        """Generate recommendations using OpenAI API."""
        if not self.client:
            return []

        doc_summary = [
            {
                "url": d.url,
                "title": d.title,
                "description": d.description,
                "word_count": d.word_count,
                "headings_count": len(d.headings),
            }
            for d in documents[:10]
        ]
        keyword_list = [kw.keyword for kw in keywords[:20]]
        cluster_topics = [c.topic_summary or "" for c in clusters[:10]]

        system_prompt = (
            "You are an SEO expert. Return ONLY JSON with key 'recommendations' as a list. "
            "Each item must have: title, description, priority(1-5), category, action_items(list)."
        )

        user_prompt = {
            "site_summary": doc_summary,
            "top_keywords": keyword_list,
            "cluster_topics": cluster_topics,
            "max_items": max_items,
        }

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_prompt)},
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        raw_recs = data.get("recommendations", [])

        recommendations: List[Recommendation] = []
        for item in raw_recs[:max_items]:
            try:
                recommendations.append(
                    Recommendation(
                        title=item.get("title", "Recommendation"),
                        description=item.get("description", ""),
                        priority=int(item.get("priority", 3)),
                        category=item.get("category", "openai"),
                        action_items=item.get("action_items", []),
                        evidence={"source": "openai"},
                    )
                )
            except Exception:
                continue

        return recommendations
