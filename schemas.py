from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Role(str, Enum):
    admin = "admin"
    manager = "manager"
    employee = "employee"


class User(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    role: Role = Role.employee
    active: bool = True


class Employee(BaseModel):
    user_id: str
    department: str
    title: Optional[str] = None


class Document(BaseModel):
    name: str
    path: str
    tags: list[str] = []
    owner_id: Optional[str] = None


class Activity(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: str = "open"
