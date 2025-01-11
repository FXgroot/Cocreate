# modules/score_calculator.py

def calculate_final_score(evaluations):
    """
    Calculates the final professionalism score for a teacher based on their MCQ correctness
    and justification evaluations.

    Args:
        evaluations (list): A list of evaluation results, each containing:
            - question (str)
            - chosen_option (int)
            - justification (str)
            - score (int): Justification score out of 10
            - feedback (str)

    Returns:
        int: The final professionalism score (out of 100).
    """
    total_questions = len(evaluations)
    if total_questions == 0:
        return 0  # Avoid division by zero if no questions are evaluated

    # Weighting factors
    mcq_weight = 0.6  # 60% weight for MCQ correctness
    justification_weight = 0.4  # 40% weight for justifications

    # Calculate MCQ correctness score
    mcq_correctness_score = 0
    justification_score = 0

    for evaluation in evaluations:
        correct_option = evaluation.get("correct_option", 0)  # Replace with correct_option logic if available
        chosen_option = evaluation["chosen_option"]
        justification_score += evaluation["score"]

        # Assuming correctness if chosen_option matches correct_option
        if chosen_option == correct_option:
            mcq_correctness_score += 1

    # Normalize scores
    mcq_score = (mcq_correctness_score / total_questions) * 100
    avg_justification_score = (justification_score / (total_questions * 10)) * 100

    # Weighted final score
    final_score = (mcq_weight * mcq_score) + (justification_weight * avg_justification_score)

    return round(final_score)


# Example usage
if __name__ == "__main__":
    # Example mock evaluation data
    evaluations = [
        {"question": "What is 2 + 2?", "chosen_option": 2, "score": 8, "correct_option": 2},
        {"question": "What is the synonym of 'happy'?", "chosen_option": 3, "score": 9, "correct_option": 3},
        {"question": "What is the capital of France?", "chosen_option": 1, "score": 7, "correct_option": 2},
    ]

    final_score = calculate_final_score(evaluations)
    print(f"Final Professionalism Score: {final_score}/100")
