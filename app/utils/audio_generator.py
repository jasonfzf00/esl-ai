import os
from fastapi import APIRouter
from sqlalchemy.orm import Session
import json
import re

from app.db.repository import GeneratedAudioRepository
from app.services.chattts_service import ChatttsService
from app.services.ollama_service import OllamaService

router = APIRouter()
ollama_service = OllamaService()
chattts_service = ChatttsService()

def clean_text_for_tts(text: str) -> str:
    """Clean text for TTS processing by removing or replacing problematic characters."""
    # Replace common punctuation with spaces or simpler versions
    text = text.replace("'", "")  # Remove apostrophes
    text = text.replace('"', "")  # Remove quotes
    text = text.replace("?", ".")  # Replace question marks with periods
    text = text.replace("!", ".")  # Replace exclamation marks with periods
    text = re.sub(r'[^\w\s.,]', '', text)  # Remove any other special characters
    return text.strip()


async def generate_audio_for_conversation(db: Session, file_id: int, conversation: dict, output_dir: str, file_basename: str):
    """
    Generate audio for a conversation and save it to the database.
    """
    try:
        # Extract conversation data
        conversation_id = conversation.get("conversation_id")
        
        # Debug the conversation structure
        print(f"Processing conversation {conversation_id}: {conversation}")
        
        # Extract text from the conversation
        # The conversation might have different structures depending on the format
        text = None
        speaker = None
        
        # Try different possible conversation structures
        if "text" in conversation:
            # Direct text field
            text = conversation["text"]
            speaker = conversation.get("speaker", "unknown")
        elif isinstance(conversation, dict) and len(conversation) > 0:
            # Format where keys are speakers and values are their lines
            # Extract the first speaker and text
            for spk, txt in conversation.items():
                if spk != "conversation_id":
                    speaker = spk
                    text = txt
                    break
        
        # Validate text
        if not text:
            print(f"No text found for conversation {conversation_id}")
            return
            
        # Clean the text for TTS processing
        cleaned_text = clean_text_for_tts(text)
        print(f"Processing text for conversation {conversation_id}: '{cleaned_text}'")
        
        # Generate audio for the cleaned text
        wav_paths = chattts_service.generateSound(
            texts=[cleaned_text],
            savePath=output_dir,
            filePrefix=f"{file_basename}_{conversation_id}_{speaker}_"
        )
        
        # Save audio file information to database
        for wav_path in wav_paths:
            print(f"Saving audio file to database: {wav_path}")
            GeneratedAudioRepository.create(
                db=db,
                generated_file_id=file_id,
                generated_filepath=wav_path,
                conversation_id=conversation_id
            )
            
    except Exception as e:
        print(f"Error generating audio for conversation {conversation_id if 'conversation_id' in conversation else 'unknown'}: {str(e)}")
        print(f"Conversation data: {conversation}")
        # Continue with other conversations even if one fails
        
async def generate_audio_in_subprocess(db: Session, file_id: int, conversation: dict, output_dir: str, file_basename: str):
    """
    Wrapper to run generate_audio_for_conversation in a separate process to avoid blocking.
    """
    import asyncio
    from concurrent.futures import ProcessPoolExecutor
    
    # Create process pool and run the audio generation
    with ProcessPoolExecutor() as pool:
        await asyncio.get_event_loop().run_in_executor(
            pool,
            generate_audio_for_conversation,
            db,
            file_id, 
            conversation,
            output_dir,
            file_basename
        )
