import json
import os
import time
import logging
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from flask import Flask, render_template, request, redirect, url_for, session
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'a3e1f8c209bcfd1c88c17f5a41b8e66cbb19c2f5f8a9c37d'


class QuestionGeneratorError(Exception):
    pass


class OllamaQuestionGenerator:
    def __init__(self, model: str = Config.OLLAMA_MODEL):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = model
        self.last_api_call = 0
        self.min_delay = 1

    def _validate_inputs(self, subject: str, experience: int) -> None:
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError("Subject must be a non-empty string")
        if not isinstance(experience, int) or experience < 0:
            raise ValueError("Experience must be a non-negative integer")

    def _rate_limit(self) -> None:
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_delay:
            time.sleep(self.min_delay - time_since_last_call)
        self.last_api_call = time.time()

    def _construct_prompt(self, subject: str, experience: int) -> str:
        return (
            f"Generate 10 multiple-choice questions on {subject} appropriate for a teacher "
            f"with {experience} years of teaching experience. Each question should:\n"
            "1. Be clear and concise\n"
            "2. Have exactly 4 options\n"
            "3. Include one correct answer and three plausible distractors\n"
            "4. Format each question as a JSON object with the following structure:\n"
            "{\n"
            '  "text": "question text",\n'
            '  "options": ["option1", "option2", "option3", "option4"],\n'
            '  "correct_option": 0  // index of correct answer (0-3)\n'
            "}\n"
            "5. Return an array of these question objects"
        )

    def _call_api(self, prompt: str) -> str:
        try:
            self._rate_limit()
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": "You are an educational expert specializing in creating assessment questions.",
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()['response']
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise QuestionGeneratorError(f"API error: {str(e)}")

    def _parse_response(self, response: str) -> List[Dict[str, any]]:
        try:
            # Find the JSON array in the response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON array found in response")

            json_str = response[start_idx:end_idx]
            questions = json.loads(json_str)

            # Validate question format
            for q in questions:
                if not all(k in q for k in ('text', 'options', 'correct_option')):
                    raise ValueError("Invalid question format")
                if len(q['options']) != 4:
                    raise ValueError("Question must have exactly 4 options")

            return questions
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return self.generate_mock_questions("default")

    def generate_questions(self, subject: str, experience: int) -> List[Dict[str, any]]:
        try:
            self._validate_inputs(subject, experience)
            prompt = self._construct_prompt(subject, experience)
            response = self._call_api(prompt)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return self.generate_mock_questions(subject)

    def generate_mock_questions(self, subject: str) -> List[Dict[str, any]]:
        # Keep the existing mock_data implementation
        mock_data = {
            "English": [
                {
                    "text": "What is the main function of a thesis statement?",
                    "options": ["To summarize the entire essay", "To present the main argument", "To list all topics",
                                "To cite sources"],
                    "correct_option": 1
                },
                {
                    "text": "Which literary device involves comparing unlike things using 'like' or 'as'?",
                    "options": ["Metaphor", "Simile", "Personification", "Alliteration"],
                    "correct_option": 1
                }
            ],
            "Math": [
                {
                    "text": "What is the result of solving the equation 2x + 5 = 13?",
                    "options": ["x = 4", "x = 6", "x = 8", "x = 3"],
                    "correct_option": 0
                },
                {
                    "text": "What is the area of a rectangle with length 6 and width 4?",
                    "options": ["24 square units", "20 square units", "10 square units", "30 square units"],
                    "correct_option": 0
                }
            ]
        }
        return mock_data.get(subject, mock_data["Math"])


# Create question generator instance
_generator = OllamaQuestionGenerator()


# Keep the rest of the main.py file the same...# Remove OPENAI_API_KEY parameter




def generate_questions(subject: str, experience: int) -> List[Dict[str, any]]:
    return _generator.generate_questions(subject, experience)


# Justification Evaluation Functions
def evaluate_justifications(questions, answers):
    evaluations = []
    for i, (question, answer) in enumerate(zip(questions, answers)):
        try:
            # Basic evaluation logic without API call
            chosen_option = int(answer['chosen_option'])
            justification = answer['justification']

            # Check if the answer is correct
            is_correct = chosen_option == question.get('correct_option', 0)

            # Basic scoring logic
            score = 7 if is_correct else 4  # Base score
            if len(justification.split()) > 20:  # Add points for detailed justification
                score += 3

            # Generate appropriate feedback
            if is_correct:
                feedback = "Good answer! " + (
                    "Your justification shows good understanding." if score > 7
                    else "Consider providing more detailed explanations."
                )
            else:
                feedback = "Review this topic further. " + (
                    "Your justification shows partial understanding." if score > 4
                    else "Try to explain your reasoning more thoroughly."
                )

            evaluations.append({
                "question": question['text'],
                "chosen_option": chosen_option,
                "justification": justification,
                "score": score,
                "feedback": feedback,
                "is_correct": is_correct
            })

        except Exception as e:
            print(f"Error evaluating question {i + 1}: {e}")
            evaluations.append({
                "question": question['text'],
                "chosen_option": answer.get('chosen_option', 0),
                "justification": answer.get('justification', ''),
                "score": 0,
                "feedback": "Your response was recorded but needs more detail for evaluation.",
                "is_correct": False
            })

    return evaluations


def parse_evaluation(evaluation_text):
    try:
        score_part, feedback_part = evaluation_text.split("Feedback:", 1)
        score = int(score_part.split("Score:")[1].split("/")[0].strip())
        feedback = feedback_part.strip()
        return score, feedback
    except Exception:
        return 0, "Could not parse the evaluation response."


# Score Calculator Function
def calculate_final_score(evaluations):
    total_questions = len(evaluations)
    if total_questions == 0:
        return 0, 0, []

    mcq_weight = 0.6
    justification_weight = 0.4

    mcq_correctness_score = sum(1 for e in evaluations if e["is_correct"])
    justification_score = sum(e["score"] for e in evaluations)
    feedback_list = [e["feedback"] for e in evaluations]

    mcq_score = (mcq_correctness_score / total_questions) * 100
    understanding_score = (justification_score / (total_questions * 10)) * 100
    final_score = (mcq_weight * mcq_score) + (justification_weight * understanding_score)

    return round(final_score), round(understanding_score), feedback_list


# Flask Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            subject = request.form.get("subject")
            experience = request.form.get("experience")

            if not subject or not experience:
                return render_template("index.html", error="Please fill in all fields")

            try:
                experience = int(experience)
                if experience < 0:
                    return render_template("index.html", error="Experience must be a positive number")
            except ValueError:
                return render_template("index.html", error="Experience must be a valid number")

            session['subject'] = subject
            session['experience'] = experience

            questions = generate_questions(subject, experience)
            if not questions:
                return render_template("index.html", error="Failed to generate questions. Please try again.")

            session['questions'] = questions
            print(f"Generated {len(questions)} questions for {subject}")

            return redirect(url_for("questions_page"))

        except Exception as e:
            print(f"Error in index route: {str(e)}")
            return render_template("index.html", error="An error occurred. Please try again.")

    return render_template("index.html")


@app.route("/questions", methods=["GET", "POST"])
def questions_page():
    if 'questions' not in session:
        print("No questions in session")
        return redirect(url_for("index"))

    questions = session['questions']
    print(f"Displaying {len(questions)} questions")

    if request.method == "POST":
        try:
            answers = []
            for i, question in enumerate(questions, 1):
                chosen_option = request.form.get(f"q{i}")
                justification = request.form.get(f"justification{i}")

                if chosen_option is None or not justification:
                    return render_template("questions.html",
                                           questions=questions,
                                           error="Please answer all questions and provide justifications")

                answer = {
                    "question": question["text"],
                    "chosen_option": chosen_option,
                    "justification": justification
                }
                answers.append(answer)

            session['answers'] = answers
            return redirect(url_for("results"))
        except Exception as e:
            print(f"Error processing question submission: {str(e)}")
            return render_template("questions.html",
                                   questions=questions,
                                   error="Error submitting answers. Please try again.")

    return render_template("questions.html", questions=questions)


@app.route("/results")
def results():
    if 'questions' not in session or 'answers' not in session:
        return redirect(url_for("index"))

    try:
        evaluations = evaluate_justifications(session['questions'], session['answers'])
        final_score, understanding_score, feedback = calculate_final_score(evaluations)

        return render_template(
            "results.html",
            subject=session.get('subject'),
            experience=session.get('experience'),
            total_questions=len(session['questions']),
            correct_answers=sum(1 for e in evaluations if e["is_correct"]),
            understanding_score=understanding_score,
            professionalism_score=final_score,
            feedback_list=feedback
        )
    except Exception as e:
        print(f"Error in results route: {str(e)}")
        return redirect(url_for("index"))


@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
