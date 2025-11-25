# app/services/scraper_service.py

import json
import os
import logging
from typing import Dict

# Setup Logger
logger = logging.getLogger("uvicorn")

# Path to the dataset
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "constitution.json")

# Global In-Memory Store
_constitution_cache :Dict[str, str] = {}

def load_constitution_data():
    """
    Loads the static JSON dataset into memory on startup.
    """
    global _constitution_cache
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                _constitution_cache = json.load(f)
            logger.info(f"✅ Loaded {_constitution_cache.keys().__len__()} chapters into memory.")
        else:
            logger.warning(f"⚠️ Constitution data file not found at {DATA_FILE}. Please run scripts/ingest.py")
    except Exception as e:
        logger.error(f"❌ Failed to load constitution data: {e}")

# Load immediately on import
load_constitution_data()

async def fetch_and_parse_url(url: str) -> str:
    """
    Retrieves the cleaned text of a constitutional chapter from the in-memory cache.
    
    Args:
        url: The URL key to look up.
    
    Returns:
        The cleaned text.
        
    Raises:
        RuntimeError: If the URL is not found in the cache (implies data drift or bad request).
    """
    # We simulate an async operation here to keep the API signature consistent
    # This allows us to swap this back to a live scraper or a DB call later without breaking the controller.
    
    if url in _constitution_cache:
        return _constitution_cache[url]
    
    # Error Handling
    error_msg = (
        f"Content for URL not found in static dataset: {url}. "
        "The system may need to re-run the ingestion script."
    )
    logger.error(error_msg)
    raise RuntimeError(error_msg)