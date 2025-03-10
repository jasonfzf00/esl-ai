# ESL AI - Vocabulary Practice Generator

A FastAPI service that processes Markdown files to generate vocabulary practice conversations using LangChain and Ollama.

## Features

- Upload Markdown files for processing
- Automatically detect grade level from filename
- Generate grade-appropriate vocabulary practice conversations
- Store results in a SQLite database
- Save generated conversations as JSON files

## Requirements

- Python 3.11+
- Ollama with a compatible LLM model (e.g., llama2)

## Installation

1. Clone this repository
2. Run the initialization script:
   ```
   python init.py
   ```
   This will:
   - Check if Python 3.11+ is installed
   - Install dependencies from requirements.txt
   - Create necessary directories
   - Create a sample Markdown file for testing
   - Check if Ollama is running

3. Make sure Ollama is running with your preferred model:
   ```
   ollama serve
   ```
   
   If you need to pull the model:
   ```
   ollama pull llama2
   ```

## Usage

1. Start the server:
   ```
   python run.py
   ```
   or
   ```
   uvicorn app.main:app --reload
   ```

For custom voice presets, stable models are available to download at https://huggingface.co/spaces/taa/ChatTTS_Speaker. 

## API Endpoints

Check http://localhost:8000/docs to check the docs, created by SwaggerUI.

## Environment Variables

The application uses the following environment variables from the `.env` file:

```
OLLAMA_MODEL=qwen2.5:0.5b
DATABASE_URL=sqlite:///./esl_ai.db
```

You can modify these values to use a different Ollama model or database connection.

## Project Structure

```
.
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Core application settings
│   ├── db/             # Database models and session
│   ├── models/         # Pydantic models
│   ├── services/       # Business logic
│   └── utils/          # Utility functions
├── output/             # Generated output files
├── .env.example        # Environment variables example
├── requirements.txt    # Project dependencies
├── init.py             # Initialization script
├── run.py              # Script to run the application
└── README.md           # Project documentation
```