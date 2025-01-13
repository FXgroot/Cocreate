# modules/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2:1b')

    # File paths
    QUESTIONS_FILE = os.path.join("data", "questions.json")
    EVALUATIONS_FILE = os.path.join("data", "results.json")
    LOGS_FILE = os.path.join("logs", "app.log")

    # Scoring weights
    MCQ_WEIGHT = 0.6
    JUSTIFICATION_WEIGHT = 0.4

    # Application settings
    MAX_QUESTIONS = 10

# Create a config instance
config = Config()
