from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Database initialization
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "app_db")

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(DATABASE_URL)
        _db = _client[DATABASE_NAME]
    return _db  # type: ignore[return-value]


# Expose db for convenience
_db_instance = get_db()
db: AsyncIOMotorDatabase = _db_instance


async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.utcnow()
    data = {**data, "created_at": now, "updated_at": now}
    result = await db[collection_name].insert_one(data)
    created = await db[collection_name].find_one({"_id": result.inserted_id})
    return created or {}


async def get_documents(
    collection_name: str,
    filter_dict: Optional[Dict[str, Any]] = None,
    limit: int = 100,
) -> list[Dict[str, Any]]:
    cursor = db[collection_name].find(filter_dict or {}).limit(limit)
    return [doc async for doc in cursor]


async def get_document_by_id(collection_name: str, id_: Any) -> Optional[Dict[str, Any]]:
    from bson import ObjectId

    try:
        oid = ObjectId(str(id_))
    except Exception:
        return None
    return await db[collection_name].find_one({"_id": oid})


async def update_document(
    collection_name: str, id_: Any, data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    from bson import ObjectId

    try:
        oid = ObjectId(str(id_))
    except Exception:
        return None
    data["updated_at"] = datetime.utcnow()
    await db[collection_name].update_one({"_id": oid}, {"$set": data})
    return await db[collection_name].find_one({"_id": oid})


async def delete_document(collection_name: str, id_: Any) -> bool:
    from bson import ObjectId

    try:
        oid = ObjectId(str(id_))
    except Exception:
        return False
    res = await db[collection_name].delete_one({"_id": oid})
    return res.deleted_count == 1
