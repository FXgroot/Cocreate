import openai
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
from config import OPENAI_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Question:
    text: str
    options: List[str]


class QuestionGeneratorError(Exception):
    """Custom exception for question generation errors"""
    pass


class QuestionGenerator:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.last_api_call = 0
        self.min_delay = 1  # Minimum delay between API calls in seconds
        openai.api_key = api_key

    def _validate_inputs(self, subject: str, experience: int) -> None:
        """Validate input parameters"""
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError("Subject must be a non-empty string")
        if not isinstance(experience, int) or experience < 0:
            raise ValueError("Experience must be a non-negative integer")

    def _rate_limit(self) -> None:
        """Implement rate limiting for API calls"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_delay:
            time.sleep(self.min_delay - time_since_last_call)
        self.last_api_call = time.time()

    def _construct_prompt(self, subject: str, experience: int) -> str:
        """Construct a detailed prompt for the API"""
        return (
            f"Generate 10 multiple-choice questions on {subject} appropriate for a teacher "
            f"with {experience} years of teaching experience. Each question should:\n"
            "1. Be clear and concise\n"
            "2. Have exactly 4 options\n"
            "3. Include one correct answer and three plausible distractors\n"
            "4. Be formatted as 'Question\nA) Option1\nB) Option2\nC) Option3\nD) Option4'"
        )

    def _call_api(self, prompt: str) -> str:
        """Make the API call with error handling"""
        try:
            self._rate_limit()
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": "You are an educational expert specializing in creating assessment questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except openai.error.RateLimitError:
            logger.error("Rate limit exceeded")
            raise QuestionGeneratorError("API rate limit exceeded. Please try again later.")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise QuestionGeneratorError(f"API error: {str(e)}")

    def generate_questions(self, subject: str, experience: int) -> List[Dict[str, any]]:
        """Generate questions with comprehensive error handling"""
        try:
            self._validate_inputs(subject, experience)
            prompt = self._construct_prompt(subject, experience)
            response = self._call_api(prompt)

            # For now, return mock questions instead of parsing API response
            return self.generate_mock_questions(subject)

        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return self.generate_mock_questions(subject)

    def generate_mock_questions(self, subject: str) -> List[Dict[str, any]]:
        """Generate mock questions for testing"""
        mock_data = {
            "English": [
                {
                    "text": "What is the main function of a thesis statement?",
                    "options": ["To summarize the entire essay", "To present the main argument", "To list all topics",
                                "To cite sources"]
                },
                {
                    "text": "Which literary device involves comparing unlike things using 'like' or 'as'?",
                    "options": ["Metaphor", "Simile", "Personification", "Alliteration"]
                }
            ],
            "Math": [
                {
                    "text": "What is the result of solving the equation 2x + 5 = 13?",
                    "options": ["x = 4", "x = 6", "x = 8", "x = 3"]
                },
                {
                    "text": "What is the area of a rectangle with length 6 and width 4?",
                    "options": ["24 square units", "20 square units", "10 square units", "30 square units"]
                }
            ]
        }

        default_questions = [
            {
                "text": "Sample question for testing purposes?",
                "options": ["Option A", "Option B", "Option C", "Option D"]
            },
            {
                "text": "Another sample question?",
                "options": ["Choice 1", "Choice 2", "Choice 3", "Choice 4"]
            }
        ]

        return mock_data.get(subject, default_questions)


# Create a singleton instance
_generator = QuestionGenerator(OPENAI_API_KEY)


def generate_questions(subject: str, experience: int) -> List[Dict[str, any]]:
    """Wrapper function to match the original interface expected by main.py"""
    return _generator.generate_questions(subject, experience)


# For testing
if __name__ == "__main__":
    test_questions = generate_questions("English", 5)
    for i, q in enumerate(test_questions, 1):
        print(f"\nQ{i}: {q['text']}")
        for j, option in enumerate(q['options'], 1):
            print(f"  {j}. {option}")