"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# Example schemas (retain for reference)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# MOVIEPLACE schemas
# --------------------------------------------------
class Content(BaseModel):
    """
    Content collection schema for movies, dramas, cartoons and others
    Collection name: "content"
    """
    title: str = Field(..., min_length=1, max_length=200)
    type: Literal["movie", "drama", "cartoon", "other"] = Field(..., description="Content category type")
    description: Optional[str] = Field(None, max_length=2000)
    year: Optional[int] = Field(None, ge=1888, le=2100)
    genres: List[str] = Field(default_factory=list)
    rating: Optional[float] = Field(None, ge=0, le=10)
    duration_minutes: Optional[int] = Field(None, ge=1, description="Duration for movies")
    episodes: Optional[int] = Field(None, ge=1, description="Episode count for series/dramas")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    video_url: Optional[str] = Field(None, description="Video or trailer URL (stream or external)")
    tags: List[str] = Field(default_factory=list)
