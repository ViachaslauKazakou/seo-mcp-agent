"""API routes for SEO Agent."""

import os
import logging
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel, Field
from sqlalchemy import func

from src.seo_agent.tools.keyword_file_parser import parse_keyword_file

from src.seo_agent.models import InputSpec, RunReport
from seo_agent.models import KeywordCandidate
from src.seo_agent.api.agent import SeoAgent
from src.seo_agent.tools.hf.clustering import Embedder, SemanticClusterer
from src.db.manager import get_db_manager
from src.db.models import (
    Website,
    AnalysisRun,
    AnalysisStatus,
    FetcherType,
    Keyword,
    KeywordCluster,
    IntentPhrase,
    IntentType,
)
from src.seo_agent.tools.hf.keywords import KeywordExtractor

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage (replace with DB in production)
agent = SeoAgent()
run_cache: dict[str, RunReport] = {}

# Template setup
template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=template_dir)


class ManualKeywordInput(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=500)
    intent: str = Field(default="informational")
    tf_idf_score: float = Field(default=1.0, ge=0.0)


class ClusterizeInput(BaseModel):
    n_clusters: int = Field(default=5, ge=1, le=30)
    model_name: str = Field(default="all-MiniLM-L6-v2")


class IntentPhraseInput(BaseModel):
    intent: str = Field(...)
    phrase: str = Field(..., min_length=1, max_length=500)
    website_id: Optional[int] = Field(default=None)


class IntentPhraseUpdate(BaseModel):
    phrase: Optional[str] = Field(default=None, min_length=1, max_length=500)
    is_active: Optional[bool] = Field(default=None)


def _to_fetcher_type(value: str) -> FetcherType:
    return FetcherType.PLAYWRIGHT if value == "playwright" else FetcherType.HTTPX


def _to_analysis_status(value: str) -> AnalysisStatus:
    return AnalysisStatus.FAILED if value == "failed" else AnalysisStatus.COMPLETED


def _to_intent_type(value: str) -> IntentType:
    value_norm = (value or "informational").strip().lower()
    for intent in IntentType:
        if intent.value == value_norm:
            return intent
    return IntentType.INFORMATIONAL


def _get_latest_run(session, website_id: int) -> Optional[AnalysisRun]:
    return (
        session.query(AnalysisRun)
        .filter(AnalysisRun.website_id == website_id)
        .order_by(AnalysisRun.started_at.desc(), AnalysisRun.id.desc())
        .first()
    )


def _get_or_create_latest_run(session, website: Website) -> AnalysisRun:
    latest_run = _get_latest_run(session, website.id)
    if latest_run is not None:
        return latest_run

    run = AnalysisRun(
        website_id=website.id,
        status=AnalysisStatus.COMPLETED,
        fetcher_type=FetcherType.HTTPX,
        urls=[f"https://{website.domain}"],
        pages_analyzed=0,
        embedding_provider="hf",
        embedding_model="all-MiniLM-L6-v2",
        max_keywords=100,
        num_clusters=5,
        total_keywords=0,
        total_clusters=0,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    session.add(run)
    session.flush()
    return run


def _get_domain_keywords_lower(session, website_id: int) -> set[str]:
    rows = (
        session.query(Keyword.keyword)
        .join(AnalysisRun, Keyword.analysis_run_id == AnalysisRun.id)
        .filter(AnalysisRun.website_id == website_id)
        .all()
    )
    return {row.keyword.strip().lower() for row in rows if row.keyword}


def _load_extra_phrases(session, website_id: int) -> dict[str, list[str]]:
    """Load active custom intent phrases for a website (global + domain-specific)."""
    rows = (
        session.query(IntentPhrase)
        .filter(
            IntentPhrase.is_active.is_(True),
            (IntentPhrase.website_id.is_(None)) | (IntentPhrase.website_id == website_id),
        )
        .all()
    )
    phrases: dict[str, list[str]] = {}
    for row in rows:
        intent_val = row.intent.value if hasattr(row.intent, "value") else str(row.intent)
        phrases.setdefault(intent_val, []).append(row.phrase)
    return phrases


def _serialize_clusters(session, analysis_run_id: int) -> list[dict]:
    clusters = (
        session.query(KeywordCluster)
        .filter(KeywordCluster.analysis_run_id == analysis_run_id)
        .order_by(KeywordCluster.cluster_label.asc(), KeywordCluster.id.asc())
        .all()
    )

    items: list[dict] = []
    for cluster in clusters:
        cluster_keywords = (
            session.query(Keyword)
            .filter(Keyword.cluster_id == cluster.id)
            .order_by(Keyword.tf_idf_score.desc(), Keyword.keyword.asc())
            .all()
        )
        
        # Compute primary intent from distribution
        intent_dist = cluster.intent_distribution or {}
        primary_intent = max(intent_dist, key=intent_dist.get) if intent_dist else "informational"
        
        items.append(
            {
                "cluster_id": cluster.id,
                "cluster_label": cluster.cluster_label,
                "cluster_name": cluster.cluster_name,
                "primary_intent": primary_intent,
                "intent_distribution": intent_dist,
                "size": cluster.size,
                "avg_tfidf_score": cluster.avg_tfidf_score,
                "top_keywords": cluster.top_keywords or [],
                "keywords": [
                    {
                        "id": kw.id,
                        "keyword": kw.keyword,
                        "intent": kw.intent.value if hasattr(kw.intent, "value") else str(kw.intent),
                        "tf_idf_score": kw.tf_idf_score,
                        "frequency": kw.frequency,
                    }
                    for kw in cluster_keywords
                ],
            }
        )
    return items


def _save_report_to_db(input_spec: InputSpec, report: RunReport) -> tuple[int, int]:
    urls = [str(url) for url in input_spec.urls]
    if not urls:
        raise ValueError("At least one URL is required")

    parsed = urlparse(urls[0])
    domain = parsed.netloc.lower()
    if not domain:
        raise ValueError(f"Invalid URL for persistence: {urls[0]}")

    db_manager = get_db_manager()
    with db_manager.session_scope() as session:
        website = session.query(Website).filter(Website.domain == domain).first()
        if website is None:
            website = Website(
                domain=domain,
                name=domain,
                language=input_spec.language,
            )
            session.add(website)
            session.flush()
        else:
            website.updated_at = datetime.utcnow()

        embedding_model = (
            input_spec.openai_embedding_model
            if input_spec.embedding_provider == "openai"
            else input_spec.hf_embedding_model
        )

        run = AnalysisRun(
            website_id=website.id,
            status=_to_analysis_status(report.status),
            fetcher_type=_to_fetcher_type(input_spec.fetcher_type),
            urls=urls,
            pages_analyzed=report.documents_parsed,
            embedding_provider=input_spec.embedding_provider,
            embedding_model=embedding_model,
            max_keywords=max(1, len(report.keywords_extracted)),
            num_clusters=max(1, len(report.clusters)),
            total_keywords=len(report.keywords_extracted),
            total_clusters=len(report.clusters),
            intent_summary=report.intent_summary,
            error_message="\n".join(report.errors) if report.errors else None,
            started_at=report.started_at,
            completed_at=report.completed_at,
        )
        session.add(run)
        session.flush()

        return website.id, run.id


@router.get("/")
async def root(request: Request):
    """Serve home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/keywords")
async def keywords_page(request: Request):
    """Serve keyword management page."""
    return templates.TemplateResponse("keywords.html", {"request": request})


@router.get("/clusters")
async def clusters_page(request: Request):
    """Serve domain clusters page."""
    return templates.TemplateResponse("clusters.html", {"request": request})


@router.get("/intents")
async def intents_page(request: Request):
    """Serve intent phrases management page."""
    return templates.TemplateResponse("intents.html", {"request": request})


# ===================== INTENT PHRASES CRUD =====================

@router.get("/api/intent-phrases")
async def list_intent_phrases(website_id: Optional[int] = None):
    """List custom intent phrases.

    Pass ``website_id`` to get only domain-specific phrases.
    Omit to get global phrases (website_id IS NULL).
    """
    try:
        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            query = session.query(IntentPhrase)
            if website_id is not None:
                query = query.filter(IntentPhrase.website_id == website_id)
            else:
                query = query.filter(IntentPhrase.website_id.is_(None))
            rows = query.order_by(IntentPhrase.intent.asc(), IntentPhrase.created_at.asc()).all()
            return {
                "items": [
                    {
                        "id": r.id,
                        "website_id": r.website_id,
                        "intent": r.intent.value if hasattr(r.intent, "value") else str(r.intent),
                        "phrase": r.phrase,
                        "is_active": r.is_active,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                    }
                    for r in rows
                ]
            }
    except Exception as e:
        logger.error("Failed to list intent phrases: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/intent-phrases", status_code=201)
async def create_intent_phrase(payload: IntentPhraseInput):
    """Create a new custom intent phrase (global or domain-specific)."""
    try:
        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            if payload.website_id is not None:
                website = session.query(Website).filter(Website.id == payload.website_id).first()
                if website is None:
                    raise HTTPException(status_code=404, detail="Website not found")
            intent = _to_intent_type(payload.intent)
            row = IntentPhrase(
                website_id=payload.website_id,
                intent=intent,
                phrase=payload.phrase.strip(),
                is_active=True,
            )
            session.add(row)
            session.flush()
            return {
                "id": row.id,
                "website_id": row.website_id,
                "intent": row.intent.value,
                "phrase": row.phrase,
                "is_active": row.is_active,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create intent phrase: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/intent-phrases/{phrase_id}")
async def update_intent_phrase(phrase_id: int, payload: IntentPhraseUpdate):
    """Update phrase text and/or active status."""
    try:
        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            row = session.query(IntentPhrase).filter(IntentPhrase.id == phrase_id).first()
            if row is None:
                raise HTTPException(status_code=404, detail="Phrase not found")
            if payload.phrase is not None:
                row.phrase = payload.phrase.strip()
            if payload.is_active is not None:
                row.is_active = payload.is_active
            session.flush()
            return {
                "id": row.id,
                "website_id": row.website_id,
                "intent": row.intent.value,
                "phrase": row.phrase,
                "is_active": row.is_active,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update intent phrase id=%s: %s", phrase_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/intent-phrases/{phrase_id}", status_code=204)
async def delete_intent_phrase(phrase_id: int):
    """Delete a custom intent phrase."""
    try:
        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            row = session.query(IntentPhrase).filter(IntentPhrase.id == phrase_id).first()
            if row is None:
                raise HTTPException(status_code=404, detail="Phrase not found")
            session.delete(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete intent phrase id=%s: %s", phrase_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/analyze")
async def analyze(input_spec: InputSpec, background_tasks: BackgroundTasks):
    """Analyze URLs and return SEO recommendations."""
    logger.info(f"Received analyze request for URLs: {input_spec.urls}")
    try:
        logger.info("Starting agent analysis...")
        report = await agent.analyze(input_spec)
        logger.info(f"Analysis completed. Report ID: {report.run_id}, Status: {report.status}")
        
        # Cache the report
        run_cache[report.run_id] = report
        logger.debug(f"Report cached with ID: {report.run_id}")

        website_id, db_run_id = _save_report_to_db(input_spec, report)
        logger.info(
            "Report persisted to DB: website_id=%s, analysis_run_id=%s, report_id=%s",
            website_id,
            db_run_id,
            report.run_id,
        )
        
        return report
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/urls")
async def list_saved_urls():
    """Return unique URLs/domains saved in DB for quick frontend selection."""
    try:
        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            websites = (
                session.query(Website)
                .order_by(Website.updated_at.desc())
                .all()
            )

            items = []
            for website in websites:
                website_url = f"https://{website.domain}"
                items.append(
                    {
                        "website_id": website.id,
                        "domain": website.domain,
                        "url": website_url,
                    }
                )

            return {"items": items}
    except Exception as e:
        logger.error("Failed to load URLs from DB: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/websites/{website_id}/runs")
async def list_website_runs(website_id: int):
    """Return recent analysis runs for selected website."""
    try:
        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            website = session.query(Website).filter(Website.id == website_id).first()
            if website is None:
                raise HTTPException(status_code=404, detail="Website not found")

            runs = (
                session.query(AnalysisRun)
                .filter(AnalysisRun.website_id == website_id)
                .order_by(AnalysisRun.started_at.desc())
                .limit(20)
                .all()
            )

            items = []
            for run in runs:
                items.append(
                    {
                        "analysis_run_id": run.id,
                        "status": run.status.value if hasattr(run.status, "value") else str(run.status),
                        "started_at": run.started_at.isoformat() if run.started_at else None,
                        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                        "pages_analyzed": run.pages_analyzed,
                        "total_keywords": run.total_keywords,
                        "total_clusters": run.total_clusters,
                        "error_message": run.error_message,
                    }
                )

            return {
                "website_id": website.id,
                "domain": website.domain,
                "items": items,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to load run history for website_id=%s: %s", website_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/websites/{website_id}/keywords")
async def list_website_keywords(website_id: int):
    """Return keywords for latest run of selected website."""
    try:
        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            website = session.query(Website).filter(Website.id == website_id).first()
            if website is None:
                raise HTTPException(status_code=404, detail="Website not found")

            latest_run = _get_latest_run(session, website.id)
            if latest_run is None:
                return {"website_id": website.id, "domain": website.domain, "analysis_run_id": None, "items": []}

            keywords = (
                session.query(Keyword)
                .filter(Keyword.analysis_run_id == latest_run.id)
                .order_by(Keyword.tf_idf_score.desc(), Keyword.keyword.asc())
                .all()
            )

            return {
                "website_id": website.id,
                "domain": website.domain,
                "analysis_run_id": latest_run.id,
                "items": [
                    {
                        "id": kw.id,
                        "keyword": kw.keyword,
                        "intent": kw.intent.value if hasattr(kw.intent, "value") else str(kw.intent),
                        "tf_idf_score": kw.tf_idf_score,
                        "frequency": kw.frequency,
                        "cluster_id": kw.cluster_id,
                    }
                    for kw in keywords
                ],
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to load keywords for website_id=%s: %s", website_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/websites/{website_id}/keywords")
async def add_website_keyword(website_id: int, payload: ManualKeywordInput):
    """Manually add keyword to latest run for selected website."""
    try:
        keyword_text = payload.keyword.strip()
        if not keyword_text:
            raise HTTPException(status_code=400, detail="Keyword cannot be empty")

        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            website = session.query(Website).filter(Website.id == website_id).first()
            if website is None:
                raise HTTPException(status_code=404, detail="Website not found")

            existing_domain_keyword = (
                session.query(Keyword)
                .join(AnalysisRun, Keyword.analysis_run_id == AnalysisRun.id)
                .filter(AnalysisRun.website_id == website.id)
                .filter(func.lower(Keyword.keyword) == keyword_text.lower())
                .first()
            )
            if existing_domain_keyword is not None:
                latest_run = _get_or_create_latest_run(session, website)
                return {
                    "analysis_run_id": latest_run.id,
                    "keyword": existing_domain_keyword.keyword,
                    "intent": (
                        existing_domain_keyword.intent.value
                        if hasattr(existing_domain_keyword.intent, "value")
                        else str(existing_domain_keyword.intent)
                    ),
                    "tf_idf_score": existing_domain_keyword.tf_idf_score,
                    "skipped": True,
                    "reason": "duplicate_for_domain",
                }

            latest_run = _get_or_create_latest_run(session, website)

            keyword_record = Keyword(
                analysis_run_id=latest_run.id,
                keyword=keyword_text,
                intent=_to_intent_type(payload.intent),
                tf_idf_score=payload.tf_idf_score,
                frequency=1,
                source_urls=[f"https://{website.domain}"],
            )
            session.add(keyword_record)

            latest_run.total_keywords = session.query(Keyword).filter(Keyword.analysis_run_id == latest_run.id).count()
            session.flush()

            return {
                "analysis_run_id": latest_run.id,
                "keyword": keyword_record.keyword,
                "intent": keyword_record.intent.value if hasattr(keyword_record.intent, "value") else str(keyword_record.intent),
                "tf_idf_score": keyword_record.tf_idf_score,
                "skipped": False,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to add keyword for website_id=%s: %s", website_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/websites/{website_id}/clusterize")
async def clusterize_website_keywords(website_id: int, payload: ClusterizeInput):
    """Run semantic clustering for latest run keywords and persist clusters."""
    try:
        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            website = session.query(Website).filter(Website.id == website_id).first()
            if website is None:
                raise HTTPException(status_code=404, detail="Website not found")

            latest_run = _get_latest_run(session, website.id)
            if latest_run is None:
                raise HTTPException(status_code=400, detail="No analysis run found for this website")

            keywords_db = (
                session.query(Keyword)
                .filter(Keyword.analysis_run_id == latest_run.id)
                .order_by(Keyword.id.asc())
                .all()
            )
            if len(keywords_db) < 2:
                raise HTTPException(status_code=400, detail="Need at least 2 keywords to run clustering")

            keyword_candidates = [
                KeywordCandidate(
                    keyword=kw.keyword,
                    frequency=kw.frequency,
                    tf_idf_score=kw.tf_idf_score,
                    intent=kw.intent.value if hasattr(kw.intent, "value") else str(kw.intent),
                    source_urls=kw.source_urls or [f"https://{website.domain}"],
                )
                for kw in keywords_db
            ]

            embedder = Embedder(model_name=payload.model_name)
            embeddings = embedder.embed_keywords(keyword_candidates)

            # Avoid silhouette-score failures when keywords count is too small
            # or requested clusters are >= number of keywords.
            if len(keyword_candidates) <= 2 or payload.n_clusters >= len(keyword_candidates):
                cluster_target = len(keyword_candidates) + 1
            else:
                cluster_target = payload.n_clusters

            clusterer = SemanticClusterer(n_clusters=cluster_target)
            clusters = clusterer.cluster(keyword_candidates, embeddings)

            session.query(Keyword).filter(Keyword.analysis_run_id == latest_run.id).update({Keyword.cluster_id: None})
            session.query(KeywordCluster).filter(KeywordCluster.analysis_run_id == latest_run.id).delete()
            session.flush()

            keyword_pool: dict[str, list[Keyword]] = {}
            for kw in keywords_db:
                keyword_pool.setdefault(kw.keyword.lower(), []).append(kw)

            for cluster in clusters:
                cluster_row = KeywordCluster(
                    analysis_run_id=latest_run.id,
                    cluster_label=cluster.cluster_id,
                    cluster_name=cluster.topic_summary,
                    size=cluster.size,
                    avg_tfidf_score=cluster.avg_tfidf,
                    top_keywords=cluster.top_keywords,
                    intent_distribution=cluster.intent_distribution,
                    centroid_embedding=cluster.centroid,
                )
                session.add(cluster_row)
                session.flush()

                for item in cluster.keywords:
                    pool = keyword_pool.get(item.keyword.lower(), [])
                    if pool:
                        kw_row = pool.pop(0)
                        kw_row.cluster_id = cluster_row.id

            latest_run.total_clusters = len(clusters)
            latest_run.num_clusters = len(clusters)
            latest_run.embedding_model = payload.model_name
            latest_run.completed_at = datetime.utcnow()
            session.flush()

            return {
                "website_id": website.id,
                "analysis_run_id": latest_run.id,
                "clusters": _serialize_clusters(session, latest_run.id),
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed clustering for website_id=%s: %s", website_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/websites/{website_id}/clusters")
async def list_website_clusters(website_id: int):
    """Return saved clusters for latest run of selected website. """
    try:
        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            website = session.query(Website).filter(Website.id == website_id).first()
            if website is None:
                raise HTTPException(status_code=404, detail="Website not found")

            latest_run = _get_latest_run(session, website.id)
            if latest_run is None:
                return {"website_id": website.id, "analysis_run_id": None, "items": []}

            return {
                "website_id": website.id,
                "analysis_run_id": latest_run.id,
                "items": _serialize_clusters(session, latest_run.id),
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to load clusters for website_id=%s: %s", website_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/collect")
async def collect_keywords(input_spec: InputSpec):
    """Fetch URL and collect keywords only (no clustering or recommendations)."""
    logger.info(f"Received collect request for URLs: {input_spec.urls}")
    try:
        result = await agent.collect(input_spec)
        keywords = result["keywords"]

        urls = [str(url) for url in input_spec.urls]
        if not urls:
            raise HTTPException(status_code=400, detail="At least one URL is required")

        parsed_url = urlparse(urls[0])
        domain = parsed_url.netloc.lower()
        if not domain:
            raise HTTPException(status_code=400, detail=f"Invalid URL: {urls[0]}")

        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            website = session.query(Website).filter(Website.domain == domain).first()
            if website is None:
                website = Website(domain=domain, name=domain, language=input_spec.language)
                session.add(website)
                session.flush()
            else:
                website.updated_at = datetime.utcnow()

            run = AnalysisRun(
                website_id=website.id,
                status=AnalysisStatus.COMPLETED if not result["errors"] else AnalysisStatus.FAILED,
                fetcher_type=_to_fetcher_type(input_spec.fetcher_type),
                urls=urls,
                pages_analyzed=result["documents_parsed"],
                embedding_provider=input_spec.embedding_provider,
                embedding_model=input_spec.hf_embedding_model,
                max_keywords=max(1, len(keywords)) if keywords else 0,
                num_clusters=0,
                total_keywords=len(keywords),
                total_clusters=0,
                intent_summary={},
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
            session.add(run)
            session.flush()

            existing_lower = _get_domain_keywords_lower(session, website.id)

            # Re-detect intent using custom phrases from DB (global + domain-specific).
            extra_phrases = _load_extra_phrases(session, website.id)
            intent_extractor = KeywordExtractor(extra_phrases=extra_phrases) if extra_phrases else None

            imported_count = 0
            skipped_count = 0

            for kw in keywords:
                keyword_norm = kw.keyword.strip().lower()
                if not keyword_norm or keyword_norm in existing_lower:
                    skipped_count += 1
                    continue

                if intent_extractor is not None:
                    detected = intent_extractor._detect_intent(kw.keyword)
                    intent_val = detected.value if hasattr(detected, "value") else str(detected)
                else:
                    intent_val = kw.intent.value if hasattr(kw.intent, "value") else str(kw.intent or "informational")

                kw_record = Keyword(
                    analysis_run_id=run.id,
                    keyword=kw.keyword,
                    intent=_to_intent_type(intent_val),
                    tf_idf_score=kw.tf_idf_score,
                    frequency=kw.frequency,
                    source_urls=[str(u) for u in (kw.source_urls or urls)],
                )
                session.add(kw_record)
                existing_lower.add(keyword_norm)
                imported_count += 1

            run.total_keywords = imported_count
            session.flush()

            return {
                "website_id": website.id,
                "analysis_run_id": run.id,
                "documents_parsed": result["documents_parsed"],
                "total_keywords": imported_count,
                "skipped_duplicates": skipped_count,
                "errors": result["errors"],
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error during keyword collection: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/keywords/{keyword_id}", status_code=204)
async def delete_keyword(keyword_id: int):
    """Delete a keyword by ID."""
    try:
        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            kw = session.query(Keyword).filter(Keyword.id == keyword_id).first()
            if kw is None:
                raise HTTPException(status_code=404, detail="Keyword not found")
            session.delete(kw)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete keyword_id=%s: %s", keyword_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/websites/{website_id}/keywords/upload")
async def upload_keywords_file(website_id: int, file: UploadFile = File(...)):
    """Upload a file (xlsx, csv, txt, docx, doc) and bulk-import keywords."""
    ALLOWED_EXTENSIONS = {"xlsx", "xlsm", "xls", "csv", "txt", "text", "md", "docx", "doc"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    filename = file.filename or "upload"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    try:
        raw_keywords = parse_keyword_file(filename, content)
    except Exception as e:
        logger.error("Failed to parse uploaded file %r: %s", filename, str(e), exc_info=True)
        raise HTTPException(status_code=422, detail=f"Failed to parse file: {str(e)}")

    if not raw_keywords:
        return {"website_id": website_id, "imported": 0, "skipped": 0, "total_keywords": 0}

    try:
        db_manager = get_db_manager()
        with db_manager.session_scope() as session:
            website = session.query(Website).filter(Website.id == website_id).first()
            if website is None:
                raise HTTPException(status_code=404, detail="Website not found")

            latest_run = _get_or_create_latest_run(session, website)

            existing_lower = _get_domain_keywords_lower(session, website.id)
            keywords_to_import = [kw_text for kw_text in raw_keywords if kw_text.lower() not in existing_lower]
            imported = len(keywords_to_import)
            skipped = len(raw_keywords) - imported

            if imported == 0:
                latest_run.total_keywords = (
                    session.query(func.count(Keyword.id))
                    .filter(Keyword.analysis_run_id == latest_run.id)
                    .scalar()
                    or 0
                )
                session.flush()
                return {
                    "website_id": website_id,
                    "analysis_run_id": latest_run.id,
                    "imported": 0,
                    "skipped": skipped,
                    "total_keywords": latest_run.total_keywords,
                }

            # Import changes keyword corpus for the run, so old cluster links
            # become stale and must be reset.
            session.query(Keyword).filter(Keyword.analysis_run_id == latest_run.id).update({Keyword.cluster_id: None})
            session.query(KeywordCluster).filter(KeywordCluster.analysis_run_id == latest_run.id).delete()
            latest_run.total_clusters = 0
            latest_run.num_clusters = 0

            extra_phrases = _load_extra_phrases(session, website.id)
            intent_extractor = KeywordExtractor(extra_phrases=extra_phrases) if extra_phrases else None

            for kw_text in keywords_to_import:
                if intent_extractor is not None:
                    detected = intent_extractor._detect_intent(kw_text)
                    intent_value = detected.value if hasattr(detected, "value") else str(detected)
                    detected_intent = _to_intent_type(intent_value)
                else:
                    detected_intent = _to_intent_type("informational")

                kw_record = Keyword(
                    analysis_run_id=latest_run.id,
                    cluster_id=None,
                    keyword=kw_text,
                    intent=detected_intent,
                    tf_idf_score=1.0,
                    frequency=1,
                    source_urls=[f"https://{website.domain}"],
                )
                session.add(kw_record)

            session.flush()
            latest_run.total_keywords = (
                session.query(func.count(Keyword.id))
                .filter(Keyword.analysis_run_id == latest_run.id)
                .scalar()
                or 0
            )
            session.flush()

            return {
                "website_id": website_id,
                "analysis_run_id": latest_run.id,
                "imported": imported,
                "skipped": skipped,
                "total_keywords": latest_run.total_keywords,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to import keywords for website_id=%s: %s", website_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/runs/{run_id}")
async def get_run(run_id: str):
    """Get analysis results by run ID."""
    if run_id not in run_cache:
        raise HTTPException(status_code=404, detail="Run not found")
    return run_cache[run_id]


@router.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
