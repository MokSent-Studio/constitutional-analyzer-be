# scripts/ingest.py

import asyncio
import json
import os
import sys
from typing import Dict, List, Optional

import httpx
from bs4 import BeautifulSoup, Tag

# Add the project root to path so we can import if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# The Target URLs
CHAPTER_URLS: List[str] = [
    "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-1-founding-provisions-04-feb",
    "https://www.gov.za/documents/constitution/chapter-2-bill-rights",
    "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-3-co-operative-government-07",
    "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-4-parliament-07-feb-1997",
    "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-5-president-and-national",
    "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-6-provinces-07-feb-1997",
    "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-7-local-government-07-feb",
    "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-8-courts-and-administration",
    "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-9-state-institutions",
    "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-10-public-administration-07",
    "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-11-security-services-07-feb",
    "https://www.gov.za/documents/notices/constitution-republic-south-africa-1996-chapter-12-traditional-leaders-07-feb",
    "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-13-finance-07-feb-1997",
    "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-14-general-provisions-07-feb",
]

OUTPUT_FILE: str = "app/data/constitution.json"

MIN_TEXT_LENGTH = 50

async def fetch_and_process(client: httpx.AsyncClient, url: str) -> Optional[str]:
    print(f"Fetching: {url}...")
    try:
        response = await client.get(url, follow_redirects=True, timeout=30.0)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Initialize variable with type hint
        main_content: Optional[Tag] = None

        # Helper to safely check if a find result is a Tag (and not None or a String)
        def get_tag(node: object) -> Optional[Tag]:
            return node if isinstance(node, Tag) else None

        # Search strategy with type narrowing
        # 1. Try 'div.field'
        candidate = soup.find('div', class_='field')
        main_content = get_tag(candidate)

        # 2. If not found, try 'main'
        if main_content is None:
            candidate = soup.find('main')
            main_content = get_tag(candidate)

        # 3. If not found, try 'body'
        if main_content is None:
            candidate = soup.body
            main_content = get_tag(candidate)

        # 4. If still None, give up
        if main_content is None:
            print(f"❌ Failed to find content container for {url}")
            return None

        # Extract text blocks
        # We explicitly look for Tags in the find_all results
        text_blocks: List[str] = []
        for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'li']):
            text_blocks.append(element.get_text(separator=' ', strip=True))

        clean_text = '\n\n'.join(text_blocks)
        
        # Validation
        if len(clean_text) < MIN_TEXT_LENGTH:
            print(f"⚠️ Text too short for {url}")
            return None

        return clean_text

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

async def main() -> None:
    # Ensure app/data exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    data_store: Dict[str, str] = {}
    
    async with httpx.AsyncClient() as client:
        # Create tasks
        tasks = [fetch_and_process(client, url) for url in CHAPTER_URLS]
        
        # Run concurrently
        results = await asyncio.gather(*tasks)
        
        # Zip and filter results
        for url, text in zip(CHAPTER_URLS, results):
            # Strict check: text must be a string (not None)
            if isinstance(text, str) and text:
                data_store[url] = text

    # Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data_store, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Ingestion complete! Saved {len(data_store)} chapters to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())