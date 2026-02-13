#!/usr/bin/env python3
"""Test script to verify av.by content fetching."""

import asyncio
from seo_agent.tools.hf.fetcher import PlayWrightFetcher
from bs4 import BeautifulSoup


async def test():
    fetcher = PlayWrightFetcher(timeout=60000, headless=False, stealth_mode=True)
    result = await fetcher.fetch('https://av.by')
    
    soup = BeautifulSoup(result.content, 'html.parser')
    
    # Check for actual content vs. block page
    title = soup.find('title')
    print(f'Title: {title.text if title else "No title"}')
    
    # Check for listings or real content
    links = soup.find_all('a', href=True)
    print(f'Total links: {len(links)}')
    
    # Check for vehicle listings
    listings = soup.find_all(['div', 'article'], class_=lambda x: x and ('listing' in x.lower() or 'card' in x.lower() or 'item' in x.lower()))
    print(f'Potential listings: {len(listings)}')
    
    # Sample first few links
    print('\nFirst 5 links:')
    for link in links[:5]:
        href = link.get('href', '')
        text = link.get_text(strip=True)[:50]
        print(f'  {text}: {href}')
    
    # Check for body content
    body = soup.find('body')
    if body:
        body_text = body.get_text(strip=True)[:200]
        print(f'\nBody preview: {body_text}...')


if __name__ == '__main__':
    asyncio.run(test())
