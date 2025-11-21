import os
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Beneficiary, Officer, MediaUpload, Review, OTPRequest, OTPVerify, SyncPayload

app = FastAPI(title="Loan Utilization Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory OTP store for demo; in production use SMS provider and expiry
OTP_STORE = {}

@app.get("/")
def read_root():
    return {"message": "Loan Utilization Tracker Backend Running"}

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

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Auth Endpoints (mobile number based)
@app.post("/auth/request-otp")
def request_otp(payload: OTPRequest):
    # Generate a simple fixed OTP for demo; replace with SMS service
    code = "123456"
    OTP_STORE[payload.phone] = {"code": code, "created_at": datetime.now(timezone.utc)}
    return {"sent": True, "code": code}

@app.post("/auth/verify-otp")
def verify_otp(payload: OTPVerify):
    record = OTP_STORE.get(payload.phone)
    if not record or record["code"] != payload.code:
        raise HTTPException(status_code=401, detail="Invalid OTP")
    return {"token": f"demo-token-{payload.phone}", "phone": payload.phone}

# Beneficiary CRUD (ingestion by State Agency/Bank)
@app.post("/beneficiaries")
def create_beneficiary(item: Beneficiary):
    inserted_id = create_document("beneficiary", item)
    return {"id": inserted_id}

@app.get("/beneficiaries")
def list_beneficiaries(state: Optional[str] = None, district: Optional[str] = None, phone: Optional[str] = None):
    filters = {}
    if state:
        filters["state"] = state
    if district:
        filters["district"] = district
    if phone:
        filters["phone"] = phone
    docs = get_documents("beneficiary", filters)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs

# Media uploads (geo-tagged, time-stamped)
@app.post("/uploads")
def create_upload(item: MediaUpload):
    # Basic validation: require some geo or timestamp
    if not item.latitude or not item.longitude:
        raise HTTPException(status_code=400, detail="Location is required")
    inserted_id = create_document("mediaupload", item)
    return {"id": inserted_id}

@app.post("/sync")
def sync_offline(payload: SyncPayload):
    # Accept list of uploads created offline
    results = []
    for it in payload.items:
        try:
            inserted_id = create_document("mediaupload", it)
            results.append({"file_name": it.file_name, "status": "ok", "id": inserted_id})
        except Exception as e:
            results.append({"file_name": it.file_name, "status": "error", "error": str(e)})
    return {"results": results}

# Reviews by officers
@app.post("/reviews")
def create_review(item: Review):
    inserted_id = create_document("review", item)
    return {"id": inserted_id}

@app.get("/reviews")
def list_reviews(upload_id: Optional[str] = None, reviewer_phone: Optional[str] = None):
    filters = {}
    if upload_id:
        try:
            filters["upload_id"] = upload_id
        except Exception:
            pass
    if reviewer_phone:
        filters["reviewer_phone"] = reviewer_phone
    docs = get_documents("review", filters)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs

# Simple AI validation placeholder endpoint
class AICheckRequest(BaseModel):
    upload_id: str

@app.post("/ai/validate")
def ai_validate(req: AICheckRequest):
    # Placeholder: in real scenario call AI service for object/scene/fraud checks
    # Here just echo success with dummy score
    return {"upload_id": req.upload_id, "valid": True, "score": 0.87, "flags": []}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
