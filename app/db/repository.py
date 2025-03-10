from sqlalchemy.orm import Session

from app.db.models import GeneratedFile, GeneratedAudio
from app.models.file import GeneratedFileCreate

class GeneratedFileRepository:
    """Repository for generated file operations."""
    
    @staticmethod
    def create(db: Session, file: GeneratedFileCreate) -> GeneratedFile:
        """
        Create a new generated file record.
        """
        db_file = db.query(GeneratedFile).filter(GeneratedFile.original_filename == file.original_filename).first()
        if db_file:
            return db_file
        else:
            db_file = GeneratedFile(
                original_filename=file.original_filename,
                generated_filepath=file.generated_filepath,
                grade_level=file.grade_level
            )
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
        return db_file
    
    @staticmethod
    def get_by_original_filename(db: Session, filename: str) -> list[GeneratedFile]:
        """
        Get generated files by original filename.
        """
        return db.query(GeneratedFile).filter(GeneratedFile.original_filename == filename).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[GeneratedFile]:
        """
        Get all generated file records.
        """
        return db.query(GeneratedFile).offset(skip).limit(limit).all()

class GeneratedAudioRepository:
    """Repository for generated audio operations."""
    
    @staticmethod
    def create(db: Session, generated_file_id: int, generated_filepath: str, conversation_id: int | None = None) -> GeneratedAudio:
        """
        Create a new generated audio record.
        """
        audio_record = db.query(GeneratedAudio).filter(GeneratedAudio.generated_filepath == generated_filepath).first()
        if audio_record:
            return audio_record
        else:
            db_audio = GeneratedAudio(
                generated_file_id=generated_file_id,
                generated_filepath=generated_filepath,
                conversation_id=conversation_id
            )
            db.add(db_audio)
            db.commit()
            db.refresh(db_audio)
            return db_audio
    
    @staticmethod
    def get_by_generated_audio_path_by_file_and_conversation_id(db: Session, generated_file_id: int, conversation_id: int) -> GeneratedAudio:
        """
        Get generated audio records by generated filepath.
        """
        return db.query(GeneratedAudio).filter(GeneratedAudio.generated_file_id == generated_file_id, GeneratedAudio.conversation_id == conversation_id).first()
