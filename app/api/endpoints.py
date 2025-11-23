# app/api/endpoints.py

from fastapi import APIRouter, HTTPException
from typing import List

# Import models, services, and utilities
from app.models.schemas import AnalysisRequest, FollowUpRequest, Chapter
from app.services import ai_service

# Create a new router instance
router = APIRouter()

# --- REVISION 1: Updated URLs to point to HTML versions ---
CHAPTERS_DATA = [
    {
        "id": 1,
        "name": "Chapter 1: Founding Provisions",
        "url": "https://www.gov.za/documents/constitution/chapter-1-founding-provisions"
    },
    {
        "id": 2,
        "name": "Chapter 2: Bill of Rights",
        "url": "https://www.gov.za/documents/constitution/chapter-2-bill-rights"
    },
    {
        "id": 3,
        "name": "Chapter 3: Co-operative Government",
        "url": "https://www.gov.za/documents/constitution/chapter-3-co-operative-government"
    },
    {
        "id": 4,
        "name": "Chapter 4: Parliament",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996-chapter-4-parliament"
    },
    {
        "id": 5,
        "name": "Chapter 5: The President & National Executive",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996-chapter-5-president-and-national-executive"
    },
    {
        "id": 6,
        "name": "Chapter 6: Provinces",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996-chapter-6-provinces"
    },
    {
        "id": 7,
        "name": "Chapter 7: Local Government",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996-chapter-7-local-government"
    },
    {
        "id": 8,
        "name": "Chapter 8: Courts & Administration of Justice",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996-chapter-8-courts-and-administration-justice"
    },
    {
        "id": 9,
        "name": "Chapter 9: State institutions supporting constitutional democracy",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996-chapter-9-state-institutions-supporting"
    },
    {
        "id": 10,
        "name": "Chapter 10: Public Administration",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996-chapter-10-public-administration"
    },
    {
        "id": 11,
        "name": "Chapter 11: Security Services",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996-chapter-11-security-services"
    },
    {
        "id": 12,
        "name": "Chapter 12: Traditional Leaders",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996-chapter-12-traditional-leaders"
    },
    {
        "id": 13,
        "name": "Chapter 13: Finance",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996-chapter-13-finance"
    },
    {
        "id": 14,
        "name": "Chapter 14: General Provisions",
        "url": "https://www.gov.za/documents/constitution-republic-south-africa-1996-chapter-14-general-provisions"
    },


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
        # Parse the raw string response from the service
        parsed_response = await ai_service.generate_initial_analysis(request)

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

        # Parse the raw string response from the service
        response_data = await ai_service.generate_follow_up_answer(request)
        return response_data

    # --- REVISION 2: Swapped status codes for ValueError and RuntimeError ---
    except ValueError as e:
        # This is for safety blocks or parsing issues.
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        # This is for network/scraping failures.
        raise HTTPException(status_code=400, detail=str(e))