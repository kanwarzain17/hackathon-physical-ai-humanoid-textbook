"""
backend/api.py - FastAPI RAG Agent API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
from dotenv import load_dotenv

# Import your agent (assuming same folder)
from .agent import BookContentAgent

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="RAG Agent API")

# CORS - very permissive for development (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class QueryResponse(BaseModel):
    response: str
    sources: List[str] = []
    session_id: Optional[str] = None
    timestamp: str
    status: str

# Simple in-memory agent manager (per session or default)
class AgentManager:
    def __init__(self):
        self.agents = {}

    def get_agent(self, session_id: Optional[str] = None):
        key = session_id or "default"
        if key not in self.agents:
            self.agents[key] = BookContentAgent()
            logger.info(f"Created new agent for session: {key}")
        return self.agents[key]

agent_manager = AgentManager()
logger.info("Agent Manager initialized successfully")

# ────────────────────────────────────────────────
# Endpoints
# ────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "RAG Agent API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "serverless": True
    }

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        agent = agent_manager.get_agent(request.session_id)
        response_text = agent.query(request.query)

        return QueryResponse(
            response=response_text,
            sources=[],               # ← fill this when you add source tracking
            session_id=request.session_id,
            timestamp=datetime.now().isoformat(),
            status="success"
        )
    except Exception as e:
        logger.error(f"Query error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# No Mangum handler needed on Vercel
# Vercel calls the 'app' object directly (ASGI)
