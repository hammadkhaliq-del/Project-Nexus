"""
User Models for Authentication
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=6)


class UserInDB(UserBase):
    """User model as stored in database"""
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    is_admin: bool = False


class User(UserBase):
    """User model for API responses (no password)"""
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Standard user response"""
    id: Optional[str] = None
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # username
    exp: datetime
    iat: datetime