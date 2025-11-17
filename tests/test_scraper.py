import pytest
# NO MORE sys.path manipulation! Pytest handles it.

# The import is clean and absolute, assuming pytest is run from the root.
from scraper_service import fetch_and_parse_url

@pytest.mark.asyncio
async def test_successful_scraping():
    """
    Tests that a valid URL returns the expected text content.
    """
    test_url = "https://www.gov.za/documents/constitution/constitution-republic-south-africa-1996-chapter-11-security-services-07-feb"
    extracted_text = await fetch_and_parse_url(test_url)
    
    assert extracted_text is not None
    assert len(extracted_text) > 500
    assert "The text below includes all amendments, up to and including the 17th Amendment to the Constitution (disclaimer)." in extracted_text

@pytest.mark.asyncio
async def test_failed_scraping_bad_url():
    """
    Tests that a 404 URL raises a RuntimeError.
    """
    test_url = "https://www.gov.za/documents/non-existent-page-12345"
    
    # pytest.raises is the correct way to test for expected exceptions
    with pytest.raises(RuntimeError) as excinfo:
        await fetch_and_parse_url(test_url)
    
    # You can even check the error message
    assert "404 Not Found" in str(excinfo.value)