from datetime import datetime
from pydantic import BaseModel, Field

class GeneratedFileBase(BaseModel):
    """Base model for generated file information."""
    original_filename: str
    generated_filepath: str
    grade_level: int

class GeneratedFileCreate(GeneratedFileBase):
    """Model for creating a generated file record."""
    pass

class GeneratedFileInDB(GeneratedFileBase):
    """Model for a generated file record in the database."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProcessResponse(BaseModel):
    """Response model for file processing."""
    success: bool
    message: str
    generated_file_id: int | None = None
    grade_level: int | None = None 
    
class ConversationResponse(BaseModel):
    """Response model for conversation."""
    generated_file_id: int
    conversations: list[dict]
    
    class Config:
        from_attributes = True
