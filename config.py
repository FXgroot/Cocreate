# modules/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    # OpenAI API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY',
                               "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")

    # File paths
    QUESTIONS_FILE = os.path.join("data", "questions.json")
    EVALUATIONS_FILE = os.path.join("data", "results.json")
    LOGS_FILE = os.path.join("logs", "app.log")

    # Scoring weights
    MCQ_WEIGHT = 0.6
    JUSTIFICATION_WEIGHT = 0.4

    # Application settings
    MAX_QUESTIONS = 10

    @classmethod
    def initialize_openai(cls):
        """Initialize OpenAI with the API key"""
        import openai
        openai.api_key = cls.OPENAI_API_KEY
        return openai


# Create a config instance
config = Config()