from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime
from app.config.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    file_path = Column(String, nullable = False)
    status = Column(String, index=True)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
