"""Data contracts for SEO Agent pipeline."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class IntentType(str, Enum):
    """Keyword intent types."""
    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"


# === INPUT ===
class InputSpec(BaseModel):
    """Agent input specification."""
    
    urls: List[HttpUrl] = Field(..., description="URLs to analyze")
    language: str = Field(default="en", description="Content language")
    max_depth: int = Field(default=0, description="Crawl depth (0=single URL)")
    max_pages: int = Field(default=50, description="Max pages to crawl")
    crawl_timeout: int = Field(default=300, description="Crawl timeout in seconds")
    
    # LLM options
    use_openai: bool = Field(default=False, description="Use OpenAI for recommendations")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model name")
    
    # HuggingFace options
    hf_embedding_model: str = Field(
        default="all-MiniLM-L6-v2", 
        description="HuggingFace embedding model name"
    )
    
    # Embedding provider
    embedding_provider: str = Field(
        default="hf",
        description="Embedding provider: 'hf' or 'openai'"
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model name"
    )
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "urls": ["https://example.com"],
            "language": "en",
            "max_depth": 1,
            "max_pages": 10,
            "use_openai": False,
            "openai_model": "gpt-4o-mini",
            "hf_embedding_model": "all-MiniLM-L6-v2",
            "embedding_provider": "hf",
            "openai_embedding_model": "text-embedding-3-small"
        }
    })


# === FETCH & PARSE ===
class FetchResult(BaseModel):
    """Result of fetching a URL."""
    
    url: str
    status_code: int
    content: str = Field(..., description="Raw HTML content")
    headers: Dict[str, str] = Field(default_factory=dict)
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None


class ParsedDocument(BaseModel):
    """Parsed and cleaned document."""
    
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    headings: List[str] = Field(default_factory=list, description="H1-H3 headings")
    main_text: str = Field(..., description="Extracted body text")
    word_count: int = 0
    parsed_at: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None


# === KEYWORDS & EMBEDDING ===
class KeywordCandidate(BaseModel):
    """Extracted keyword with scores."""
    
    keyword: str
    frequency: int = Field(..., description="Raw frequency count")
    tf_idf_score: float = Field(..., description="TF-IDF score")
    intent: Optional[IntentType] = None
    source_urls: List[str] = Field(default_factory=list, description="Where found")


class EmbeddingRecord(BaseModel):
    """Vector representation of text."""
    
    text: str = Field(..., description="Original text (keyword or chunk)")
    embedding: List[float] = Field(..., description="Vector [768-dim for sentence-transformers]")
    source_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# === CLUSTERING ===
class Cluster(BaseModel):
    """Semantic cluster of keywords."""
    
    cluster_id: int
    keywords: List[KeywordCandidate] = Field(...)
    centroid: List[float] = Field(..., description="Cluster center embedding")
    cohesion_score: float = Field(..., description="Silhouette score (0-1)")
    topic_summary: Optional[str] = None
    suggested_content_topics: List[str] = Field(default_factory=list)


# === RECOMMENDATIONS ===
class Recommendation(BaseModel):
    """SEO recommendation with source."""
    
    id: str = Field(default_factory=lambda: "rec_" + str(datetime.utcnow().timestamp()))
    title: str
    description: str
    priority: int = Field(ge=1, le=5, description="1=low, 5=critical")
    category: str = Field(..., description="on-page, structure, keywords, etc.")
    source_urls: List[str] = Field(default_factory=list, description="Evidence URLs")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Supporting data")
    action_items: List[str] = Field(default_factory=list)


# === OUTPUT ===
class RunReport(BaseModel):
    """Final SEO analysis report."""
    
    run_id: str = Field(default_factory=lambda: "run_" + str(datetime.utcnow().timestamp()))
    input_spec: InputSpec
    status: str = Field(default="completed", description="completed, partial, failed")
    
    # Results
    documents_parsed: int
    keywords_extracted: List[KeywordCandidate]
    clusters: List[Cluster]
    recommendations: List[Recommendation]
    
    # Metadata
    started_at: datetime
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    errors: List[str] = Field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        """Execution time in seconds."""
        return (self.completed_at - self.started_at).total_seconds()
