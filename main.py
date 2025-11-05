from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, db, get_document_by_id, get_documents, update_document
from schemas import Activity, Document, Employee, User

app = FastAPI(title="InnovaIndustria API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    time: datetime


@app.get("/test", response_model=HealthResponse)
async def test() -> HealthResponse:
    # A simple db touch to ensure connection works
    _ = await db.command("ping")
    return HealthResponse(status="ok", time=datetime.utcnow())


# Generic helpers
async def list_items(collection: str, limit: int = 100):
    docs = await get_documents(collection, limit=limit)
    for d in docs:
        d["id"] = str(d.pop("_id"))
        if "created_at" in d:
            d["created_at"] = d["created_at"].isoformat()
        if "updated_at" in d:
            d["updated_at"] = d["updated_at"].isoformat()
    return docs


async def create_item(collection: str, data: Dict[str, Any]):
    created = await create_document(collection, data)
    if not created:
        raise HTTPException(status_code=400, detail="Failed to create")
    created["id"] = str(created.pop("_id"))
    if "created_at" in created:
        created["created_at"] = created["created_at"].isoformat()
    if "updated_at" in created:
        created["updated_at"] = created["updated_at"].isoformat()
    return created


# Users
@app.get("/users")
async def get_users():
    return await list_items("user")


@app.post("/users")
async def create_user(user: User):
    return await create_item("user", user.model_dump())


# Employees
@app.get("/employees")
async def get_employees():
    return await list_items("employee")


@app.post("/employees")
async def create_employee(employee: Employee):
    return await create_item("employee", employee.model_dump())


# Documents
@app.get("/documents")
async def get_docs():
    return await list_items("document")


@app.post("/documents")
async def create_doc(doc: Document):
    return await create_item("document", doc.model_dump())


# Activities
@app.get("/activities")
async def get_activities():
    return await list_items("activity")


@app.post("/activities")
async def create_activity(activity: Activity):
    return await create_item("activity", activity.model_dump())
