"""Fetcher tool: download and parse content from URLs."""

import asyncio
import httpx
from datetime import datetime
from typing import Optional

from seo_agent.models import FetchResult, ParsedDocument
from seo_agent.tools.hf.stealth_config import STEALTH_JS, STEALTH_BROWSER_ARGS

# Anti-bot headers to bypass simple bot detection
ANTI_BOT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0",
    "Referer": "https://www.google.com/",
}


class PlayWrightFetcher:
    """Parse URL with Playwright for JavaScript-heavy sites with anti-bot bypass."""
    
    def __init__(
        self, 
        timeout: int = 60000, 
        headless: bool = False,
        stealth_mode: bool = True
    ):
        """Initialize Playwright fetcher.
        
        Args:
            timeout: Request timeout in milliseconds (default: 60000ms = 60s)
            headless: Run browser in headless mode (default: False for better detection bypass)
            stealth_mode: Enable stealth mode to hide automation (default: True)
        """
        self.timeout = timeout
        self.headless = headless
        self.stealth_mode = stealth_mode
        self._browser = None
    
    async def fetch(self, url: str) -> FetchResult:
        """Fetch content from URL using Playwright with anti-detection measures.
        
        Handles JavaScript-heavy sites, Cloudflare, Turnstile, and other bot detection.
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return FetchResult(
                url=url,
                status_code=0,
                content="",
                error="Playwright not installed. Install with: pip install playwright"
            )
        
        try:
            async with async_playwright() as p:
                # Launch browser with enhanced stealth args
                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=STEALTH_BROWSER_ARGS
                )
                
                try:
                    # Create context with realistic browser fingerprint
                    context = await browser.new_context(
                        extra_http_headers=ANTI_BOT_HEADERS,
                        user_agent=ANTI_BOT_HEADERS["User-Agent"],
                        viewport={"width": 1920, "height": 1080},
                        locale="en-US",
                        timezone_id="America/New_York",
                        # Simulate real browser permissions
                        permissions=["geolocation"],
                        geolocation={"latitude": 40.7128, "longitude": -74.0060},
                        color_scheme="light",
                    )
                    
                    # Add comprehensive stealth JS
                    if self.stealth_mode:
                        await context.add_init_script(STEALTH_JS)
                    
                    page = await context.new_page()
                    
                    # Navigate to URL with timeout
                    response = await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=self.timeout
                    )
                    
                    if response is None:
                        return FetchResult(
                            url=url,
                            status_code=0,
                            content="",
                            error="Failed to load page"
                        )
                    
                    status_code = response.status
                    
                    # Wait for content to load (adaptive wait)
                    try:
                        await page.wait_for_load_state("networkidle", timeout=10000)
                    except:
                        # If networkidle times out, continue anyway
                        pass
                    
                    # Additional wait for dynamic content and anti-bot checks
                    await page.wait_for_timeout(3000)
                    
                    # Simulate human behavior - mouse movement
                    try:
                        await page.mouse.move(100, 100)
                        await page.mouse.move(200, 200)
                    except:
                        pass
                    
                    # Get page content (after JavaScript execution)
                    content = await page.content()
                    
                    # Extract response headers
                    headers = dict(response.headers)
                    
                    await context.close()
                    
                    return FetchResult(
                        url=str(response.url),
                        status_code=status_code,
                        content=content,
                        headers=headers,
                    )
                finally:
                    await browser.close()
                    
        except Exception as e:
            return FetchResult(
                url=url,
                status_code=0,
                content="",
                error=f"Playwright error: {str(e)}"
            )


class Fetcher:
    """Fetch HTML content from URLs using httpx."""
    
    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None):
        self.timeout = timeout
        self.user_agent = user_agent or ANTI_BOT_HEADERS["User-Agent"]
        self.headers = {
            k: v for k, v in ANTI_BOT_HEADERS.items() 
            if k != "User-Agent"
        }
    
    async def fetch(self, url: str) -> FetchResult:
        """Fetch content from URL using httpx."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers={**self.headers, "User-Agent": self.user_agent},
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
