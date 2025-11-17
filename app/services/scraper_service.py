import httpx
from bs4 import BeautifulSoup

async def fetch_and_parse_url(url: str) -> str:
    """
    Asynchronously fetches content from a URL, parses the HTML,
    and extracts clean, readable text from the main content area.
    Args:
        url: The URL of the webpage to scrape.

    Returns:
        A string containing the cleaned text of the main content.

    Raises:
        RuntimeError: If the network request fails, the page is not found,
                    or no meaningful content can be extracted.
    """
    print(f"Attempting to scrape URL: {url}")
    try:
        # 1. Asynchronously fetch the HTML content
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=15.0)
            # Raise an exception for HTTP errors like 404 Not Found or 500 Server Error
            response.raise_for_status()

        # 2. Parse the HTML with BeautifulSoup and the fast lxml parser
        soup = BeautifulSoup(response.text, 'lxml')

        # 3. Find the main content container
        # This is based on our detective work. We add fallbacks to make it more robust.
        main_content = soup.find('div', class_='field') or soup.find('main') or soup.body
        if not main_content:
            raise ValueError("Could not find a main content container in the HTML.")

        # 4. Extract text from relevant tags (paragraphs, headings, list items)
        # The 'separator' ensures words aren't mashed together. 'strip' removes extra whitespace.
        text_blocks = [
            p.get_text(separator=' ', strip=True) 
            for p in main_content.find_all(['p', 'h1', 'h2', 'h3', 'li'])
        ]
        document_text = '\n\n'.join(text_blocks)

        # 5. Validate that we actually got meaningful content
        if not document_text or len(document_text) < 200: # Increased threshold
            raise ValueError(f"Extracted text is too short ({len(document_text)} chars) to be valid content.")

        print("Scraping successful.")
        return document_text

    except httpx.RequestError as e:
        # Catches network-related errors (DNS, connection refused, etc.)
        raise RuntimeError(f"A network error occurred while trying to fetch the URL: {e}") from e
    except httpx.HTTPStatusError as e:
        # Catches bad HTTP status codes
        raise RuntimeError(f"The URL returned a bad status code: {e.response.status_code} {e.response.reason_phrase}") from e
    except ValueError as e:
        # Catches our own validation errors
        raise RuntimeError(f"Failed to process the page content: {e}") from e
    except Exception as e:
        # A general catch-all for any other unexpected errors
        raise RuntimeError(f"An unexpected error occurred during scraping: {e}") from e