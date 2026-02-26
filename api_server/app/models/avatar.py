from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Avatar(Base):
    __tablename__ = "avatars"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String) # Historic, Modern, Custom
    image_url = Column(String)
    voice_url = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
