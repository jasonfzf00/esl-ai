import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import json
import re
import time

from app.core.config import settings
from app.db.session import get_db
from app.db.repository import GeneratedFileRepository, GeneratedAudioRepository
from app.models.file import GeneratedFileCreate, ProcessResponse, ConversationResponse
from app.services.ollama_service import OllamaService
from app.utils.file_processing import (
    extract_grade_from_filename,
    ensure_output_directory,
    save_json_response
)
from app.utils.audio_generator import generate_audio_for_conversation, generate_audio_in_subprocess


router = APIRouter()
ollama_service = OllamaService()

@router.post("/generate-conversation", response_model=ProcessResponse)
async def generate_conversation(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Process a Markdown file and generate conversation.
    """
    try:
        # Check if file is a Markdown file
        if not file.filename.endswith('.md'):
            raise HTTPException(
                status_code=400,
                detail="Only Markdown (.md) files are supported"
            )

        # Read file content
        content = await file.read()
        markdown_text = content.decode('utf-8')
        
        # Extract grade level from filename
        grade_level = extract_grade_from_filename(file.filename)
        
        # Create output directory
        file_basename = os.path.splitext(file.filename)[0]
        output_dir = os.path.join(settings.OUTPUT_DIR, file_basename)
        ensure_output_directory(output_dir)

        words = ollama_service.pick_words(markdown_text, grade_level)
        result = ollama_service.generate_conversation_from_words(words, grade_level)
        
        combined_results = {
            "words": words,
            "conversations": result["conversation"]
        }
        
        # Path and filename for the generated JSON file
        output_filename = f"{file_basename}_generated.json"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save file path to database
        file_record = GeneratedFileRepository.create(
            db=db,
            file=GeneratedFileCreate(
                original_filename=file_basename,
                generated_filepath=output_path,
                grade_level=grade_level
            )
        )
        
        # Add conversation_id to each conversation and generate audio
        conversation_id = 0
        for conversation in result["conversation"]:
            conversation_id += 1
            conversation["conversation_id"] = conversation_id
            # Generate audio in the background
            print(f"Generating audio for conversation {conversation_id}")
            # background_tasks.add_task(test)
            background_tasks.add_task(
                generate_audio_in_subprocess,
                db=db,
                file_id=file_record.id,
                conversation=conversation,
                output_dir=output_dir,
                file_basename=file_basename
            )
        
        # Save combined results to JSON file
        save_json_response(output_path, combined_results)
        
        return ProcessResponse(
            success=True,
            message="File processed successfully",
            generated_file_id=file_record.id,
            grade_level=grade_level
        )
        
    except Exception as e:
        return ProcessResponse(
            success=False,
            message=f"Error processing file: {str(e)}"
        ) 
        
@router.get("/conversation/{generated_file_id}")
async def get_conversation_by_generated_file_id(
    generated_file_id: int, db: Session = Depends(get_db)):
    """
    Get a conversation by its ID.
    """
    # file_basename = os.path.splitext(file_name)[0] # remove file extension
    conversation_record = GeneratedFileRepository.get_by_generated_file_id(db, generated_file_id)
    if not conversation_record:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )
    # Load conversation from generated file
    with open(conversation_record.generated_filepath, 'r') as f:
        conversation_data = json.load(f)
    
    # Add generated file ID to response
    conversation_data["generated_file_id"] = generated_file_id
    
    return ConversationResponse(
        generated_file_id=generated_file_id,
        conversations=conversation_data["conversations"]
    )   

@router.get("/conversation/{generated_file_id}/audio/{conversation_id}",
            response_class=FileResponse)
async def get_audio_file_by_conversation_id(
    generated_file_id: int,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get audio for a conversation by its ID.
    """
    audio_record = GeneratedAudioRepository.get_by_generated_audio_path_by_file_and_conversation_id(
        db, generated_file_id, conversation_id)
    if not audio_record:
        raise HTTPException(
            status_code=404,
            detail=f"Audio file for conversation {conversation_id} not found"
        )
        
    audio_path = audio_record.generated_filepath
    return FileResponse(audio_path)