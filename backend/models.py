from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    nickname = Column(String)
    avatar = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    capsules = relationship("Capsule", back_populates="owner")
    likes = relationship("Like", back_populates="user")

class Capsule(Base):
    __tablename__ = "capsules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Store tags as comma separated string for simplicity in SQLite
    tags = Column(String, nullable=True) 
    
    weblink = Column(String, nullable=True)
    extension = Column(String, nullable=True)
    llm_analysis = Column(String, nullable=True)

    owner = relationship("User", back_populates="capsules")
    media_items = relationship("Media", back_populates="capsule")
    likes = relationship("Like", back_populates="capsule")

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    capsule_id = Column(Integer, ForeignKey("capsules.id"))
    media_type = Column(String) # image, video, audio
    file_path = Column(String)
    
    capsule = relationship("Capsule", back_populates="media_items")

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    capsule_id = Column(Integer, ForeignKey("capsules.id"))

    user = relationship("User", back_populates="likes")
    capsule = relationship("Capsule", back_populates="likes")
