#!/usr/bin/env python3
"""
Book Content RAG Agent
- Cohere embeddings (embed-english-v3.0)
- Qdrant vector search
- Cohere for text generation
- Strictly answers ONLY from retrieved book content
"""
import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
import cohere
from qdrant_client import QdrantClient

# --------------------------------------------------
# ENV & LOGGING
# --------------------------------------------------
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("book-rag")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION_NAME", "book_embeddings")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise RuntimeError("COHERE_API_KEY is missing")  # This is fine – fails fast locally

# --------------------------------------------------
# BOOK CONTENT AGENT
# --------------------------------------------------
class BookContentAgent:
    def __init__(self):
        self.cohere_client = None
        self.qdrant = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Lazy init – only called when first needed"""
        if self.cohere_client is None:
            logger.info("Initializing Cohere client...")
            self.cohere_client = cohere.Client(COHERE_API_KEY)
            logger.info("Cohere client initialized")

        if self.qdrant is None:
            logger.info("Initializing Qdrant client...")
            if QDRANT_URL:
                self.qdrant = QdrantClient(
                    url=QDRANT_URL,
                    api_key=QDRANT_API_KEY,
                    timeout=30
                )
            else:
                self.qdrant = QdrantClient(
                    host=os.getenv("QDRANT_HOST", "localhost"),
                    port=int(os.getenv("QDRANT_PORT", 6333))
                )
            # Test connection
            self.qdrant.get_collections()
            logger.info(f"Connected to Qdrant collection: {QDRANT_COLLECTION}")

    def query(self, user_input: str) -> str:
        try:
            self._initialize_clients()  # Ensure clients are ready

            # Simple greeting check
            greetings = ['hello', 'hi', 'hey', 'good morning', 'good evening', 'good afternoon']
            if user_input.lower().strip() in greetings:
                return "Hello! I'm your Book Assistant. Ask me anything about ROS 2, humanoid robotics, or the course material!"

            # Simple off-topic check
            off_topic_keywords = [
                'weather','joke','funny','news','sports','movie','celebrity','crypto',
                'recipe','food','travel','music','song','tv','shopping','price',
                'health','medical','exercise','diet'
            ]
            if any(k in user_input.lower() for k in off_topic_keywords):
                return ("I can only answer questions related to the book content. "
                        "Please ask about robotics, ROS 2, or the course material.")

            # Get embeddings
            embed_response = self.cohere_client.embed(
                texts=[user_input],
                model="embed-english-v3.0",
                input_type="search_query"
            )
            query_vector = embed_response.embeddings[0]

            # Search Qdrant
            hits = self.qdrant.search(
                collection_name=QDRANT_COLLECTION,
                query_vector=query_vector,
                limit=5,
                with_payload=True
            )

            retrieved_content = []
            for hit in hits:
                score = float(hit.score or 0.0)
                if score >= 0.3:
                    text = hit.payload.get("content", "")
                    if text.strip():
                        retrieved_content.append({"content": text[:800], "score": score})

            logger.info(f"Retrieved {len(retrieved_content)} excerpts")

            if not retrieved_content:
                return "No relevant book content found. Try asking about ROS 2 or humanoid robotics."

            # Build RAG prompt
            context = "\n\n---\n\n".join([f"[Excerpt {i+1}]:\n{item['content']}" for i, item in enumerate(retrieved_content)])
            rag_prompt = f"""You are a helpful assistant that answers questions ONLY using the provided book excerpts below.
BOOK EXCERPTS:
{context}
USER QUESTION: {user_input}
INSTRUCTIONS:
- Answer ONLY using information from the book excerpts above.
- If relevant, summarize clearly.
- Do NOT use outside knowledge.
- Keep concise and accurate.
ANSWER:"""

            # Generate
            generation_response = self.cohere_client.chat(
                model="command-a-03-2025",  # ← This model is still active as of Jan 2026 (strongest in Command family)
                message=rag_prompt,
                temperature=0.2,
                max_tokens=500
            )

            answer = generation_response.text
            return answer.strip() if answer else "No response generated. Try again."

        except Exception as e:
            logger.exception(f"RAG query error: {e}")
            return "Sorry, I encountered an error processing your request. Please try again."

    def reset(self):
        pass

# --------------------------------------------------
# LOCAL TEST
# --------------------------------------------------
if __name__ == "__main__":
    agent = BookContentAgent()
    response = agent.query("What is ROS 2?")
    print(response)
