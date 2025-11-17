# app/main.py

from fastapi import FastAPI
from app.api import endpoints

# Initialize the FastAPI application
app = FastAPI(
    title="Constitution Analyzer API",
    description="API for providing AI-powered analysis of the South African Constitution.",
    version="1.0.0"
)

# Include the router from our endpoints file, prefixing all routes with /api
app.include_router(endpoints.router, prefix="/api")

@app.get("/", tags=["Root"])
async def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the Constitution Analyzer API"}