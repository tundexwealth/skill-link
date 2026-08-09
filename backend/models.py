from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from db.base import Base
    
    
class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    
    area = Column(String)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    address = Column(String, nullable=True)
    
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)
    
    description = Column(String, nullable=False)
    
    image_url = Column(String, nullable=False)
    
    services = relationship(
        "Service",
        back_populates="category"
    )

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    description = Column(Text)
    price = Column(String)

    location_id = Column(
        Integer,
        ForeignKey("locations.id")
    )
    location = relationship("Location")
    
    provider_id = Column(
        Integer,
        ForeignKey("providers.id")
    )

    provider = relationship(
        "Provider",
        back_populates="services"
    )
    
    category_id = Column(
    Integer,
    ForeignKey("categories.id")
    )
    category = relationship(
        "Category",
        back_populates="services"
    )
    
class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    business_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    website = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    about = Column(Text, nullable=True)
    logo_url = Column(String, nullable=True)
    cover_image = Column(String, nullable=True)
    email = Column(String, nullable=True)
    is_imported = Column(Boolean, nullable=False, default=False)
    imported_from = Column(String, nullable=True)
    verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="provider")

    services = relationship(
        "Service",
        back_populates="provider"
    )
    
    ratings = relationship(
        "Rating",
        back_populates="provider",
        foreign_keys="Rating.provider_id"
    )
    
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    provider = relationship("Provider", back_populates="user", uselist=False)


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    provider = relationship("Provider", back_populates="ratings", foreign_keys=[provider_id])


class ClaimRequest(Base):
    __tablename__ = "claim_requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    provider = relationship("Provider")


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
