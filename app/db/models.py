from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base

class GeneratedFile(Base):
    """Model for storing information about generated files."""
    __tablename__ = "generated_files"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, index=True)
    generated_filepath = Column(String, unique=True, index=True)
    grade_level = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<GeneratedFile(id={self.id}, original_filename='{self.original_filename}')>" 
    
class GeneratedAudio(Base):
    """Model for storing information about generated audio files."""
    __tablename__ = "generated_audios"

    id = Column(Integer, primary_key=True, index=True)
    generated_file_id = Column(Integer, ForeignKey("generated_files.id"))
    generated_filepath = Column(String, unique=True, index=True)
    conversation_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<GeneratedAudio(id={self.id}, generated_file_id='{self.generated_file_id}')>" 
    