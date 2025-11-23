# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints

# Initialize the FastAPI application
app = FastAPI(
    title="Constitution Analyzer API",
    description="API for providing AI-powered analysis of the South African Constitution.",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",  # The default URL for the Vue dev server
    "http://127.0.0.1:5173",
    "https://constitutional-analyzer-fe.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allow requests from our frontend
    allow_credentials=True,      # Allow cookies (good for future auth)
    allow_methods=["*"],         # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],         # Allow all headers
)

# Include the router from our endpoints file, prefixing all routes with /api
app.include_router(endpoints.router, prefix="/api")

@app.get("/", tags=["Root"])
async def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the Constitution Analyzer API"}