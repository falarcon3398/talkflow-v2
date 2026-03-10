from sqlalchemy import Column, String, DateTime
from app.database import Base
from datetime import datetime
import uuid

class Voice(Base):
    __tablename__ = "voices"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    voice_url = Column(String) # URL to access the .wav file
    created_at = Column(DateTime, default=datetime.utcnow)
