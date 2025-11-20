import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Content

app = FastAPI(title="MOVIEPLACE API", description="Backend for MOVIEPLACE content platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContentCreate(Content):
    pass

class ContentOut(BaseModel):
    id: str
    title: str
    type: str
    description: Optional[str] = None
    year: Optional[int] = None
    genres: List[str] = []
    rating: Optional[float] = None
    duration_minutes: Optional[int] = None
    episodes: Optional[int] = None
    poster_url: Optional[str] = None
    video_url: Optional[str] = None
    tags: List[str] = []

    class Config:
        from_attributes = True


def serialize_doc(doc: dict) -> ContentOut:
    return ContentOut(
        id=str(doc.get("_id")),
        title=doc.get("title"),
        type=doc.get("type"),
        description=doc.get("description"),
        year=doc.get("year"),
        genres=doc.get("genres", []),
        rating=doc.get("rating"),
        duration_minutes=doc.get("duration_minutes"),
        episodes=doc.get("episodes"),
        poster_url=doc.get("poster_url"),
        video_url=doc.get("video_url"),
        tags=doc.get("tags", []),
    )


@app.get("/")
def read_root():
    return {"message": "MOVIEPLACE API is running"}


@app.get("/api/content", response_model=List[ContentOut])
def list_content(
    type: Optional[str] = Query(None, description="Filter by type: movie, drama, cartoon, other"),
    q: Optional[str] = Query(None, description="Search in title and description"),
    limit: int = Query(50, ge=1, le=100)
):
    filter_dict = {}
    if type:
        filter_dict["type"] = type
    if q:
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"genres": {"$elemMatch": {"$regex": q, "$options": "i"}}},
            {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}},
        ]
    docs = get_documents("content", filter_dict, limit)
    return [serialize_doc(d) for d in docs]


@app.post("/api/content", response_model=dict)
def create_content(payload: ContentCreate):
    try:
        new_id = create_document("content", payload)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
