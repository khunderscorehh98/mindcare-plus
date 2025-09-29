from pydantic import BaseModel, EmailStr
from typing import List, Optional

class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True

class ChatTurn(BaseModel):
    role: str
    content: str

class ChatIn(BaseModel):
    message: str
    history: Optional[List[ChatTurn]] = []

class ChatOut(BaseModel):
    reply: str

class CheckInIn(BaseModel):
    mood: str
    stress_level: int
    notes: Optional[str] = None

class CheckInOut(BaseModel):
    id: int
    mood: str
    stress_level: int
    notes: Optional[str]
    created_at: str

class ResourceOut(BaseModel):
    title: str
    desc: Optional[str]
    url: str

