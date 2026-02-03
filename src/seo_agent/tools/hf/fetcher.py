"""Fetcher tool: download and parse content from URLs."""

import httpx
from datetime import datetime
from typing import Optional

from seo_agent.models import FetchResult, ParsedDocument


class Fetcher:
    """Fetch HTML content from URLs."""
    
    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None):
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    
    async def fetch(self, url: str) -> FetchResult:
        """Fetch content from URL."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.user_agent},
                    follow_redirects=True
                )
                
                return FetchResult(
                    url=str(response.url),
                    status_code=response.status_code,
                    content=response.text,
                    headers=dict(response.headers),
                )
        except Exception as e:
            return FetchResult(
                url=url,
                status_code=0,
                content="",
                error=str(e)
            )


class Parser:
    """Parse HTML to extract text and structure."""
    
    def __init__(self):
        import trafilatura
        self.trafilatura = trafilatura
    
    def parse(self, fetch_result: FetchResult) -> ParsedDocument:
        """Parse fetched content using trafilatura."""
        if fetch_result.error or fetch_result.status_code != 200:
            return ParsedDocument(
                url=fetch_result.url,
                main_text="",
                error=fetch_result.error or f"HTTP {fetch_result.status_code}"
            )
        
        try:
            # Extract main content
            main_text = self.trafilatura.extract(fetch_result.content) or ""
            
            # Try to extract title and description
            from bs4 import BeautifulSoup
            
            # Use html.parser as fallback if lxml is not available
            try:
                soup = BeautifulSoup(fetch_result.content, "lxml")
            except:
                soup = BeautifulSoup(fetch_result.content, "html.parser")
            
            title = None
            if soup.title:
                title = soup.title.string
            
            description = None
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                description = meta_desc["content"]
            
            # Extract headings
            headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
            
            return ParsedDocument(
                url=fetch_result.url,
                title=title,
                description=description,
                headings=headings,
                main_text=main_text,
                word_count=len(main_text.split()),
                error=None
            )
        except Exception as e:
            return ParsedDocument(
                url=fetch_result.url,
                main_text="",
                error=f"Parse error: {str(e)}"
            )
