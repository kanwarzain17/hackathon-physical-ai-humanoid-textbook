"""
backend/api.py - FastAPI RAG Agent API
"""

import os
import traceback
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv
import logging

# ────────────────────────────────────────────────
# Debug prints at module level (runs on cold start / import)
# These will show in Vercel logs even if logging fails
# ────────────────────────────────────────────────
print("=== backend/api.py MODULE STARTED LOADING ON VERCEL ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path includes current dir: {os.path.abspath('.') in os.sys.path}")

# Load environment variables
load_dotenv()
print("Environment variables loaded via dotenv")

# Quick env var visibility check (without revealing full keys)
print(f"QDRANT_URL exists: {'QDRANT_URL' in os.environ}")
print(f"QDRANT_API_KEY exists: {'QDRANT_API_KEY' in os.environ}")
print(f"COHERE_API_KEY exists: {'COHERE_API_KEY' in os.environ}")
print(f"OPENROUTER_API_KEY exists: {'OPENROUTER_API_KEY' in os.environ}")

# Logging setup
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
logger.info("Logging initialized")

# Import your agent (this line often fails → catch it early)
try:
    from .agent import BookContentAgent
    print("Successfully imported BookContentAgent from .agent")
except Exception as import_err:
    print(f"CRITICAL: Failed to import BookContentAgent: {str(import_err)}")
    traceback.print_exc()
    logger.critical("Import of BookContentAgent failed", exc_info=True)
    raise  # re-raise so Vercel sees the crash

# FastAPI app
app = FastAPI(title="RAG Agent API")

# CORS - permissive for development
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

# Agent manager
class AgentManager:
    def __init__(self):
        self.agents = {}
        print("AgentManager initialized (global instance created)")

    def get_agent(self, session_id: Optional[str] = None):
        key = session_id or "default"
        if key not in self.agents:
            print(f"Creating new BookContentAgent for session: {key}")
            self.agents[key] = BookContentAgent()
            logger.info(f"Created new agent for session: {key}")
        else:
            print(f"Reusing existing agent for session: {key}")
        return self.agents[key]

# Global agent manager instance
agent_manager = AgentManager()
print("Global agent_manager instance created")

# ────────────────────────────────────────────────
# Endpoints
# ────────────────────────────────────────────────

@app.get("/")
async def root():
    print("GET / called")
    return {"message": "RAG Agent API is running"}

@app.get("/health")
async def health_check():
    print("GET /health called")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "serverless": True
    }

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    print(f"POST /query received | query: '{request.query}' | session: {request.session_id}")

    if not request.query.strip():
        print("Empty query → returning 400")
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        print("Attempting to get/create agent...")
        agent = agent_manager.get_agent(request.session_id)
        print("Agent ready → executing query...")

        response_text = agent.query(request.query)
        print("Query executed successfully")

        return QueryResponse(
            response=response_text,
            sources=[],  # fill this when you add source tracking
            session_id=request.session_id,
            timestamp=datetime.now().isoformat(),
            status="success"
        )

    except Exception as e:
        error_msg = f"Query endpoint failed: {str(e)}"
        print(error_msg)
        traceback.print_exc()           # full traceback to stdout → Vercel logs
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

print("=== backend/api.py LOADING COMPLETED SUCCESSFULLY ===")
