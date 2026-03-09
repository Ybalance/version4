from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Media
class MediaBase(BaseModel):
    media_type: str
    file_path: str

class MediaCreate(MediaBase):
    pass

class Media(MediaBase):
    id: int
    capsule_id: int

    class Config:
        from_attributes = True

# Capsule
class CapsuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None
    is_public: bool = True
    tags: Optional[str] = None
    weblink: Optional[str] = None
    extension: Optional[str] = None
    llm_analysis: Optional[str] = None

class CapsuleCreate(CapsuleBase):
    media_items: List[MediaCreate] = []

class Capsule(CapsuleBase):
    id: int
    owner_id: int
    created_at: datetime
    media_items: List[Media] = []
    likes_count: int = 0
    is_liked_by_me: bool = False # Field for UI logic
    owner_nickname: str = ""

    class Config:
        from_attributes = True

# User
class UserBase(BaseModel):
    phone: str
    nickname: Optional[str] = None # Make nickname optional for login if reused

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    avatar: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone: Optional[str] = None
