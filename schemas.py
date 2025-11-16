"""
Database Schemas for KFUPM Cybersecurity Club

Each Pydantic model here maps to a MongoDB collection (collection name is the lowercase of the class name).

Collections:
- member: Club members and roles
- event: Club events (upcoming and past)
- registration: Event registrations
- message: Contact messages
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class Member(BaseModel):
    full_name: str = Field(..., description="Member full name")
    email: EmailStr = Field(..., description="KFUPM email")
    role: str = Field(..., description="Role or position in the club (e.g., President, Core Team, Member)")
    avatar_url: Optional[str] = Field(None, description="Avatar/profile image URL")
    bio: Optional[str] = Field(None, description="Short member bio")
    linkedin: Optional[str] = Field(None, description="LinkedIn URL")
    twitter: Optional[str] = Field(None, description="Twitter/X URL")


class Event(BaseModel):
    title: str = Field(..., description="Event title")
    description: str = Field(..., description="Event description")
    start_time: datetime = Field(..., description="Event start datetime (UTC)")
    end_time: datetime = Field(..., description="Event end datetime (UTC)")
    location: str = Field(..., description="Event location or online link")
    banner_url: Optional[str] = Field(None, description="Banner/cover image URL")
    tags: List[str] = Field(default_factory=list, description="Tags like workshop, CTF, talk")


class Registration(BaseModel):
    event_id: str = Field(..., description="Event ObjectId as string")
    full_name: str = Field(..., description="Registrant full name")
    email: EmailStr = Field(..., description="Registrant email")
    student_id: Optional[str] = Field(None, description="Student ID")
    comments: Optional[str] = Field(None, description="Additional notes")


class Message(BaseModel):
    full_name: str = Field(..., description="Sender name")
    email: EmailStr = Field(..., description="Sender email")
    subject: str = Field(..., description="Message subject")
    message: str = Field(..., description="Message body")
