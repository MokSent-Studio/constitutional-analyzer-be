# app/api/endpoints.py

from fastapi import APIRouter, HTTPException
from typing import List

# Import models, services, and utilities
from app.models.schemas import AnalysisRequest, FollowUpRequest, Chapter
from app.services import ai_service
from app.utils import parsers

# Create a new router instance
router = APIRouter()

# --- REVISION 1: Updated URLs to point to HTML versions ---
CHAPTERS_DATA = [
    {
        "id": 1,
        "name": "Chapter 1: Founding Provisions",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996/chapter-1-founding-provisions"
    },
    {
        "id": 2,
        "name": "Chapter 2: Bill of Rights",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996/chapter-2-bill-rights"
    },
    {
        "id": 3,
        "name": "Chapter 3: Co-operative Government",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996/chapter-3-co-operative-government"
    }
]

@router.get("/chapters", response_model=List[Chapter], tags=["Chapters"])
async def get_chapters():
    """
    Provides the frontend with a static list of the constitutional chapters.
    """
    return CHAPTERS_DATA

@router.post("/analyze", tags=["Analysis"])
async def analyze_chapter(request: AnalysisRequest):
    """
    Receives a request to analyze a chapter, calls the AI service,
    and returns a structured analysis.
    """
    try:
        # Call the appropriate service function
        raw_json_response = await ai_service.generate_initial_analysis(request)

        # Parse the raw string response from the service
        parsed_response = parsers.extract_json_from_string(raw_json_response)

        # If parsing fails, raise a 500 server error
        if parsed_response is None:
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error: The AI service returned a malformed response."
            )

        # Return the parsed dictionary on success
        return parsed_response

    # --- REVISION 2: Swapped status codes for ValueError and RuntimeError ---
    except ValueError as e:
        # This is for safety blocks or parsing issues.
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        # This is for network/scraping failures.
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/follow-up", tags=["Analysis"])
async def follow_up_question(request: FollowUpRequest):
    """
    Receives a follow-up question, calls the AI service with context,
    and returns a concise answer.
    """
    try:
        # Call the appropriate service function
        raw_json_response = await ai_service.generate_follow_up_answer(request)

        # Parse the raw string response from the service
        parsed_response = parsers.extract_json_from_string(raw_json_response)

        # If parsing fails, raise a 500 server error
        if parsed_response is None:
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error: The AI service returned a malformed response."
            )
        
        # Return the parsed dictionary on success
        return parsed_response

    # --- REVISION 2: Swapped status codes for ValueError and RuntimeError ---
    except ValueError as e:
        # This is for safety blocks or parsing issues.
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        # This is for network/scraping failures.
        raise HTTPException(status_code=400, detail=str(e))