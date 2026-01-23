# backend/api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from mangum import Mangum
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
from dotenv import load_dotenv

# Import your agent
from agent import BookContentAgent  # make sure agent.py is accessible

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="RAG Agent API")

# CORS
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
    def get_agent(self, session_id=None):
        if session_id is None:
            if "default" not in self.agents:
                self.agents["default"] = BookContentAgent()
            return self.agents["default"]
        if session_id not in self.agents:
            self.agents[session_id] = BookContentAgent()
        return self.agents[session_id]

agent_manager = AgentManager()
logger.info("Agent Manager initialized successfully")

# Endpoints
@app.get("/")
async def root():
    return {"message": "RAG Agent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    agent = agent_manager.get_agent(request.session_id)
    response_text = agent.query(request.query)
    return QueryResponse(
        response=response_text,
        sources=[],
        session_id=request.session_id,
        timestamp=datetime.now().isoformat(),
        status="success"
    )

# Mangum handler for Vercel
handler = Mangum(app)