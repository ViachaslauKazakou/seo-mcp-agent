"""Database models for SEO MCP Agent."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
import enum


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class IntentType(enum.Enum):
    """Keyword intent types."""
    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"


class FetcherType(enum.Enum):
    """Fetcher types."""
    HTTPX = "httpx"
    PLAYWRIGHT = "playwright"


class AnalysisStatus(enum.Enum):
    """Analysis run status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ==================== WEBSITE ====================
class Website(Base):
    """Website configuration and access details."""
    
    __tablename__ = "websites"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Basic info
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Repository info
    repo_url: Mapped[Optional[str]] = mapped_column(String(500))
    repo_path: Mapped[Optional[str]] = mapped_column(String(500))
    repo_branch: Mapped[Optional[str]] = mapped_column(String(100), default="main")
    
    # SSH access for hosting
    ssh_host: Mapped[Optional[str]] = mapped_column(String(255))
    ssh_port: Mapped[Optional[int]] = mapped_column(Integer, default=22)
    ssh_user: Mapped[Optional[str]] = mapped_column(String(100))
    ssh_key_path: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Settings
    language: Mapped[str] = mapped_column(String(10), default="en")
    country: Mapped[Optional[str]] = mapped_column(String(10))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis_runs: Mapped[List["AnalysisRun"]] = relationship("AnalysisRun", back_populates="website", cascade="all, delete-orphan")
    serp_positions: Mapped[List["SerpPosition"]] = relationship("SerpPosition", back_populates="website", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Website(id={self.id}, domain='{self.domain}')>"


# ==================== ANALYSIS RUN ====================
class AnalysisRun(Base):
    """Analysis run metadata."""
    
    __tablename__ = "analysis_runs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    website_id: Mapped[int] = mapped_column(Integer, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Run details
    status: Mapped[AnalysisStatus] = mapped_column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    fetcher_type: Mapped[FetcherType] = mapped_column(SQLEnum(FetcherType), default=FetcherType.HTTPX)
    
    # URLs analyzed
    urls: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    pages_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    
    # Settings used
    embedding_provider: Mapped[str] = mapped_column(String(50), default="hf")
    embedding_model: Mapped[str] = mapped_column(String(100))
    max_keywords: Mapped[int] = mapped_column(Integer, default=100)
    num_clusters: Mapped[int] = mapped_column(Integer, default=10)
    
    # Summary stats
    total_keywords: Mapped[int] = mapped_column(Integer, default=0)
    total_clusters: Mapped[int] = mapped_column(Integer, default=0)
    
    # Intent distribution
    intent_summary: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Error info
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    website: Mapped["Website"] = relationship("Website", back_populates="analysis_runs")
    keywords: Mapped[List["Keyword"]] = relationship("Keyword", back_populates="analysis_run", cascade="all, delete-orphan")
    clusters: Mapped[List["KeywordCluster"]] = relationship("KeywordCluster", back_populates="analysis_run", cascade="all, delete-orphan")
    page_analyses: Mapped[List["PageAnalysis"]] = relationship("PageAnalysis", back_populates="analysis_run", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_analysis_runs_website_created', 'website_id', 'started_at'),
    )
    
    def __repr__(self) -> str:
        return f"<AnalysisRun(id={self.id}, website_id={self.website_id}, status={self.status.value})>"


# ==================== KEYWORDS ====================
class Keyword(Base):
    """Extracted keywords with metrics."""
    
    __tablename__ = "keywords"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    cluster_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("keyword_clusters.id", ondelete="SET NULL"))
    
    # Keyword data
    keyword: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    intent: Mapped[IntentType] = mapped_column(SQLEnum(IntentType), nullable=False)
    
    # Metrics
    tf_idf_score: Mapped[float] = mapped_column(Float, nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, default=1)
    
    # Embedding (for vector search)
    embedding: Mapped[Optional[List[float]]] = mapped_column(ARRAY(Float))
    
    # Source URLs
    source_urls: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="keywords")
    cluster: Mapped[Optional["KeywordCluster"]] = relationship("KeywordCluster", back_populates="keywords")
    
    __table_args__ = (
        Index('ix_keywords_analysis_intent', 'analysis_run_id', 'intent'),
        Index('ix_keywords_analysis_tfidf', 'analysis_run_id', 'tf_idf_score'),
    )
    
    def __repr__(self) -> str:
        return f"<Keyword(id={self.id}, keyword='{self.keyword}', intent={self.intent.value})>"


# ==================== KEYWORD CLUSTERS ====================
class KeywordCluster(Base):
    """Semantic clusters of keywords."""
    
    __tablename__ = "keyword_clusters"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Cluster info
    cluster_label: Mapped[int] = mapped_column(Integer, nullable=False)
    cluster_name: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Statistics
    size: Mapped[int] = mapped_column(Integer, default=0)
    avg_tfidf_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Top keywords
    top_keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # Intent distribution
    intent_distribution: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Centroid embedding
    centroid_embedding: Mapped[Optional[List[float]]] = mapped_column(ARRAY(Float))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="clusters")
    keywords: Mapped[List["Keyword"]] = relationship("Keyword", back_populates="cluster")
    
    __table_args__ = (
        Index('ix_clusters_analysis_label', 'analysis_run_id', 'cluster_label'),
    )
    
    def __repr__(self) -> str:
        return f"<KeywordCluster(id={self.id}, label={self.cluster_label}, size={self.size})>"


# ==================== SERP RESULTS ====================
class SerpResult(Base):
    """SERP analysis results."""
    
    __tablename__ = "serp_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Query info
    query: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    country: Mapped[str] = mapped_column(String(10), default="US")
    
    # SERP data
    total_results: Mapped[Optional[int]] = mapped_column(Integer)
    featured_snippet: Mapped[Optional[dict]] = mapped_column(JSONB)
    people_also_ask: Mapped[Optional[List[dict]]] = mapped_column(JSONB)
    related_searches: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # Top results
    top_results: Mapped[Optional[List[dict]]] = mapped_column(JSONB)
    
    # Timestamps
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    positions: Mapped[List["SerpPosition"]] = relationship("SerpPosition", back_populates="serp_result", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_serp_query_date', 'query', 'fetched_at'),
    )
    
    def __repr__(self) -> str:
        return f"<SerpResult(id={self.id}, query='{self.query}')>"


# ==================== SERP POSITIONS ====================
class SerpPosition(Base):
    """Website position tracking in SERP."""
    
    __tablename__ = "serp_positions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    website_id: Mapped[int] = mapped_column(Integer, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    serp_result_id: Mapped[int] = mapped_column(Integer, ForeignKey("serp_results.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Position data
    position: Mapped[Optional[int]] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500))
    snippet: Mapped[Optional[str]] = mapped_column(Text)
    
    # Ranking info
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    in_top_10: Mapped[bool] = mapped_column(Boolean, default=False)
    in_top_3: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    website: Mapped["Website"] = relationship("Website", back_populates="serp_positions")
    serp_result: Mapped["SerpResult"] = relationship("SerpResult", back_populates="positions")
    
    __table_args__ = (
        Index('ix_positions_website_date', 'website_id', 'checked_at'),
        Index('ix_positions_serp_position', 'serp_result_id', 'position'),
    )
    
    def __repr__(self) -> str:
        return f"<SerpPosition(id={self.id}, position={self.position}, url='{self.url}')>"


# ==================== PAGE ANALYSIS ====================
class PageAnalysis(Base):
    """Individual page analysis results."""
    
    __tablename__ = "page_analyses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Page info
    url: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Content metrics
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    main_text_length: Mapped[int] = mapped_column(Integer, default=0)
    
    # Extracted data
    keywords_found: Mapped[int] = mapped_column(Integer, default=0)
    main_content: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metadata
    meta_description: Mapped[Optional[str]] = mapped_column(Text)
    meta_keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # Headers
    h1_tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    h2_tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # Status
    fetch_success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="page_analyses")
    
    __table_args__ = (
        Index('ix_pages_analysis_url', 'analysis_run_id', 'url'),
    )
    
    def __repr__(self) -> str:
        return f"<PageAnalysis(id={self.id}, url='{self.url}')>"
