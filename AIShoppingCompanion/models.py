from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Additional search filters")

class Product(BaseModel):
    id: str = Field(..., description="Unique product identifier")
    title: str = Field(..., description="Product title")
    description: str = Field(..., description="Product description")
    price: str = Field(..., description="Product price")
    currency: str = Field(default="₹", description="Currency symbol")
    image_url: str = Field(..., description="Product image URL")
    rating: Optional[float] = Field(default=None, description="Product rating (0-5)")
    reviews_count: Optional[int] = Field(default=None, description="Number of reviews")
    availability: str = Field(default="In Stock", description="Product availability")
    source: str = Field(..., description="Source website")
    url: str = Field(..., description="Product URL")
    relevance_score: float = Field(..., description="AI-calculated relevance score (0-1)")
    explanation: str = Field(..., description="Why this product was recommended")

class SearchResponse(BaseModel):
    query: str = Field(..., description="Original search query")
    products: List[Product] = Field(default=[], description="List of recommended products")
    explanation: str = Field(..., description="Overall explanation of the search results")
    search_id: str = Field(..., description="Unique search identifier")
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatMessage(BaseModel):
    content: str = Field(..., description="Chat message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class ChatResponse(BaseModel):
    message: str = Field(..., description="AI agent response")
    has_products: bool = Field(default=False, description="Whether response includes product recommendations")
    products: List[Product] = Field(default=[], description="Product recommendations if applicable")
    timestamp: datetime = Field(default_factory=datetime.now)
