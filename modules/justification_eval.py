import openai
from config import OPENAI_API_KEY

# Initialize OpenAI API key
openai.api_key = OPENAI_API_KEY

def evaluate_justifications(questions, answers):
    """
    Evaluates the justifications provided by the teacher for their answers.

    Args:
        questions (list): List of questions with options and correct answers.
        answers (list): List of teacher's answers and justifications.

    Returns:
        list: A list of evaluation results, including justification scores and feedback.
    """
    evaluations = []

    for question, answer in zip(questions, answers):
        try:
            # Construct the prompt dynamically based on the question and answer
            prompt = (
                f"Question: {question['text']}\n"
                f"Chosen Option: {question['options'][answer['chosen_option'] - 1]}\n"
                f"Justification: {answer['justification']}\n\n"
                "Evaluate the justification. Provide a score out of 10 based on the depth, relevance, "
                "and understanding demonstrated. Provide a brief feedback comment."
            )

            # Use OpenAI's API to evaluate the justification
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are an educational evaluator."},
                          {"role": "user", "content": prompt}],
                max_tokens=100
            )

            # Extract the evaluation from the response
            evaluation_text = response["choices"][0]["message"]["content"]
            score, feedback = parse_evaluation(evaluation_text)

            evaluations.append({
                "question": question['text'],
                "chosen_option": answer['chosen_option'],
                "justification": answer['justification'],
                "score": score,
                "feedback": feedback
            })

        except Exception as e:
            print(f"Error evaluating justification: {e}")
            evaluations.append({
                "question": question['text'],
                "chosen_option": answer['chosen_option'],
                "justification": answer['justification'],
                "score": 0,
                "feedback": "Evaluation could not be completed due to an error."
            })

    return evaluations


def parse_evaluation(evaluation_text):
    """
    Parses the evaluation text to extract a score and feedback.

    Args:
        evaluation_text (str): The raw evaluation response from the LLM.

    Returns:
        tuple: A tuple containing the score (int) and feedback (str).
    """
    try:
        # Example expected response: "Score: 8/10. Feedback: The justification demonstrates a good understanding."
        score_part, feedback_part = evaluation_text.split("Feedback:", 1)
        score = int(score_part.split("Score:")[1].split("/")[0].strip())
        feedback = feedback_part.strip()
        return score, feedback
    except Exception:
        return 0, "Could not parse the evaluation response."


# Example usage
if __name__ == "__main__":
    # Example mock data
    questions = [
        {"text": "What is the synonym of 'happy'?", "options": ["Sad", "Angry", "Joyful", "Tired"]},
        {"text": "What is 2 + 2?", "options": ["3", "4", "5", "6"]}
    ]
    answers = [
        {"chosen_option": 3, "justification": "Because 'joyful' is a synonym for 'happy'."},
        {"chosen_option": 2, "justification": "Basic arithmetic tells us that 2 + 2 equals 4."}
    ]

    results = evaluate_justifications(questions, answers)
    for result in results:
        print(f"Question: {result['question']}")
        print(f"Score: {result['score']}/10")
        print(f"Feedback: {result['feedback']}\n")
