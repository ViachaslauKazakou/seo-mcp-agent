"""FastAPI application entrypoint."""

import logging
from fastapi import FastAPI

from seo_agent.api.routers import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="SEO Agent API",
    description="Autonomous SEO analysis and recommendations",
    version="0.1.0",
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
