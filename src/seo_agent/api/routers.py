"""API routes for SEO Agent."""

import os
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from src.seo_agent.models import InputSpec, RunReport
from src.seo_agent.api.agent import SEOAgent

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage (replace with DB in production)
agent = SEOAgent()
run_cache: dict[str, RunReport] = {}

# Template setup
template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=template_dir)


@router.get("/")
async def root(request: Request):
    """Serve home page."""
    return templates.TemplateResponse("index.html", {"request": request})


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
        
        # Try to serialize to ensure it's JSON-compatible
        logger.debug("Serializing report to JSON...")
        report_dict = report.model_dump()
        logger.debug(f"Report serialized successfully")
        
        return report
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
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
