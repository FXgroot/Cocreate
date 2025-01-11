# modules/database_handler.py

import json
import os


def save_to_file(filename, data):
    """
    Saves data to a JSON file.

    Args:
        filename (str): The name of the file to save the data.
        data (any): The data to be saved (must be JSON-serializable).
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving data to {filename}: {e}")


def load_from_file(filename):
    """
    Loads data from a JSON file.

    Args:
        filename (str): The name of the file to load the data.

    Returns:
        any: The loaded data, or None if an error occurs.
    """
    try:
        if not os.path.exists(filename):
            print(f"File {filename} does not exist.")
            return None

        with open(filename, "r") as file:
            data = json.load(file)
        print(f"Data successfully loaded from {filename}")
        return data
    except Exception as e:
        print(f"Error loading data from {filename}: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Example data
    sample_questions = [
        {"text": "What is 2 + 2?", "options": ["3", "4", "5", "6"]},
        {"text": "What is the synonym of 'happy'?", "options": ["Sad", "Angry", "Joyful", "Tired"]}
    ]
    filename = "data/sample_questions.json"

    # Save the sample data
    save_to_file(filename, sample_questions)

    # Load the data back
    loaded_data = load_from_file(filename)
    print("Loaded Data:", loaded_data)


'''
# app.py

from flask import Flask, render_template, request, redirect, url_for
from modules.question_generator import generate_questions
from modules.justification_eval import evaluate_justifications
from modules.score_calculator import calculate_final_score

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Serve login or home page

@app.route('/questions', methods=['POST', 'GET'])
def questions():
    if request.method == 'POST':
        subject = request.form['subject']
        experience = request.form['experience']
        questions = generate_questions(subject)
        return render_template('questions.html', questions=questions)

    return render_template('questions.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    answers = request.form.getlist('answers')  # Assuming answers come as a list
    justifications = request.form.getlist('justifications')  # Justifications for each answer

    # Assuming you have the correct answers available (could be fetched from DB or static)
    evaluations = evaluate_justifications(answers, justifications)
    final_score = calculate_final_score(evaluations)

    return render_template('result.html', score=final_score)

if __name__ == '__main__':
    app.run(debug=True)

'''