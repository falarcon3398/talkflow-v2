from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, index=True, nullable=True) # Celery task ID
    type = Column(String) # text_to_video or audio_to_video
    status = Column(String, default="queued") # queued, processing, completed, failed
    progress = Column(Integer, default=0)
    result_url = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    title = Column(String, nullable=True)
    project_id = Column(String, nullable=True, index=True)
    params = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
