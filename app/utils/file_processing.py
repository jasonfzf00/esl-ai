import os
import re
import json
import markdown
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_grade_from_filename(filename: str) -> int:
    """
    Extract grade level from filename.
    
    Examples:
    - "3rd-animal-madness-with-professor-aligator_ANIMA.md" -> 3
    - "5th_grade_science_lesson.md" -> 5
    - "no_grade_info.md" -> 8 (default)
    """
    # Look for patterns like "3rd", "5th", "7th", etc.
    grade_pattern = re.compile(r'(\d+)(?:st|nd|rd|th)')
    match = grade_pattern.search(filename)
    
    # If found, return the grade number
    if match:
        return int(match.group(1))
    
    # Alternative pattern: "grade_5", "grade-7", etc.
    alt_pattern = re.compile(r'grade[_\-](\d+)')
    match = alt_pattern.search(filename)
    
    if match:
        return int(match.group(1))
    
    # Default to 8th grade if no grade is detected
    return 8

def ensure_output_directory(directory_path: str) -> None:
    """
    Ensure the output directory exists.
    """
    os.makedirs(directory_path, exist_ok=True)

def save_json_response(output_path: str, data: dict) -> str:
    """
    Save JSON response to a file.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the data to a JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_path 

# def process_markdown_text(markdown_text: str) -> list[str]:
#     """
#     Process markdown text and split it into chunks.
#     """
#     # Convert markdown to HTML
#     html = markdown.markdown(markdown_text)
    
#     # Parse HTML and extract text
#     soup = BeautifulSoup(html, 'html.parser')
#     text = soup.get_text()
    
#     # Split text into chunks
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=100,
#         length_function=len,
#     )
    
#     chunks = text_splitter.split_text(text)
#     return chunks