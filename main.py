import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Member, Event, Registration, Message

app = FastAPI(title="KFUPM Cybersecurity Club API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "KFUPM Cybersecurity Club API is running"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
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
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# Utility converters
class EventOut(BaseModel):
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    banner_url: Optional[str] = None
    tags: List[str] = []


def serialize_event(doc) -> EventOut:
    return EventOut(
        id=str(doc.get("_id")),
        title=doc.get("title"),
        description=doc.get("description"),
        start_time=doc.get("start_time"),
        end_time=doc.get("end_time"),
        location=doc.get("location"),
        banner_url=doc.get("banner_url"),
        tags=doc.get("tags", []),
    )


# Routes: Members (read-only for site)
@app.get("/api/members", response_model=List[Member])
def list_members():
    docs = get_documents("member", {})
    # Convert _id to string-safe via pydantic ignoring unknown
    return [Member(**{k: v for k, v in d.items() if k in Member.model_fields}) for d in docs]


# Routes: Events
@app.get("/api/events", response_model=List[EventOut])
def list_events(status: Optional[str] = None):
    now = datetime.utcnow()
    filt = {}
    if status == "upcoming":
        filt = {"end_time": {"$gte": now}}
    elif status == "past":
        filt = {"end_time": {"$lt": now}}
    docs = get_documents("event", filt)
    return [serialize_event(d) for d in docs]


@app.post("/api/events", status_code=201)
def create_event(event: Event):
    event_id = create_document("event", event)
    return {"id": event_id}


# Routes: Event registrations
@app.post("/api/events/{event_id}/register", status_code=201)
def register_event(event_id: str, reg: Registration):
    try:
        _ = ObjectId(event_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid event id")

    data = reg.model_dump()
    data["event_id"] = event_id
    new_id = create_document("registration", data)
    return {"id": new_id}


# Routes: Contact messages
@app.post("/api/contact", status_code=201)
def send_message(msg: Message):
    new_id = create_document("message", msg)
    return {"id": new_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
