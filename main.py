import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from schemas import Volunteer, DonationPledge, ContactMessage
from database import create_document, get_documents, db

app = FastAPI(title="Green Future Initiative API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Green Future Initiative Backend", "version": "1.0.0"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

# Schema exposure for internal tooling
class SchemaInfo(BaseModel):
    name: str
    fields: List[str]

@app.get("/schema")
def get_schema():
    return {
        "volunteer": [f for f in Volunteer.model_fields.keys()],
        "contactmessage": [f for f in ContactMessage.model_fields.keys()],
        "donationpledge": [f for f in DonationPledge.model_fields.keys()],
    }

# Health and DB test
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
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
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

# -----------------------------
# Volunteer Endpoints
# -----------------------------
@app.post("/api/volunteers")
def create_volunteer(payload: Volunteer):
    try:
        inserted_id = create_document("volunteer", payload)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/volunteers")
def list_volunteers(limit: Optional[int] = 50):
    try:
        docs = get_documents("volunteer", {}, limit or 50)
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Donation Endpoints
# -----------------------------
@app.post("/api/donations")
def create_donation(payload: DonationPledge):
    try:
        inserted_id = create_document("donationpledge", payload)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/donations")
def list_donations(limit: Optional[int] = 50):
    try:
        docs = get_documents("donationpledge", {}, limit or 50)
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Contact Messages
# -----------------------------
@app.post("/api/contacts")
def create_contact(payload: ContactMessage):
    try:
        inserted_id = create_document("contactmessage", payload)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts")
def list_contacts(limit: Optional[int] = 50):
    try:
        docs = get_documents("contactmessage", {}, limit or 50)
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
