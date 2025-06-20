from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
from services import AIShoppingService
from models import SearchRequest, SearchResponse, ChatMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Shopping Agent", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize AI Shopping Service
ai_service = AIShoppingService()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main application page"""
    with open("static/index.html", "r") as file:
        return HTMLResponse(content=file.read())

@app.post("/api/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """
    Search for products based on natural language query
    """
    try:
        logger.info(f"Received search request: {request.query}")
        
        # Process the search query through AI services
        result = await ai_service.process_search_query(request.query)
        
        return SearchResponse(
            query=request.query,
            products=result.get("products", []),
            explanation=result.get("explanation", ""),
            search_id=result.get("search_id", "")
        )
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/chat")
async def chat_with_agent(message: ChatMessage):
    """
    Handle conversational queries with the AI agent
    """
    try:
        logger.info(f"Received chat message: {message.content}")
        
        # Generate session ID (in real app, this would come from user session)
        session_id = "user_session"
        
        # Process chat message through AI services
        response = await ai_service.process_chat_message(message.content, session_id)
        
        return {
            "response": response.get("message", "I'm sorry, I couldn't process your request."),
            "has_products": response.get("has_products", False),
            "products": response.get("products", []),
            "filter_options": response.get("filter_options", []),
            "filter_name": response.get("filter_name", ""),
            "timestamp": response.get("timestamp")
        }
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Shopping Agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
