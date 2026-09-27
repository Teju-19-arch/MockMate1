def evaluate_answer(answer, question):
    """
    Evaluate one technical-test answer.
    """

    answer = (answer or "").strip()

    if not answer:
        return {
            "technical_accuracy": 0,
            "relevance": 0,
            "completeness": 0,
            "communication": 0,
            "overall_score": 0,
            "feedback": "No answer provided."
        }

    words = answer.split()
    word_count = len(words)

    # -----------------------------
    # COMPLETENESS
    # -----------------------------

    if word_count >= 80:
        completeness = 95
    elif word_count >= 50:
        completeness = 85
    elif word_count >= 30:
        completeness = 75
    elif word_count >= 15:
        completeness = 60
    else:
        completeness = 40

    # -----------------------------
    # COMMUNICATION
    # -----------------------------

    sentences = [
        s.strip()
        for s in answer.replace("!", ".")
        .replace("?", ".")
        .split(".")
        if s.strip()
    ]

    if len(sentences) >= 4:
        communication = 90
    elif len(sentences) >= 3:
        communication = 82
    elif len(sentences) >= 2:
        communication = 75
    else:
        communication = 60

    # -----------------------------
    # RELEVANCE
    # -----------------------------

    question_words = {
        word.lower()
        for word in question.split()
        if len(word) > 4
    }

    answer_words = {
        word.lower()
        for word in answer.split()
        if len(word) > 4
    }

    matching_words = question_words & answer_words

    relevance = min(
        95,
        55 + len(matching_words) * 5
    )

    # -----------------------------
    # TECHNICAL ACCURACY
    # -----------------------------

    technical_keywords = [
        "algorithm",
        "model",
        "data",
        "database",
        "api",
        "python",
        "machine learning",
        "training",
        "testing",
        "accuracy",
        "validation",
        "classification",
        "regression",
        "neural network",
        "docker",
        "fastapi",
        "react",
        "sql",
        "nlp",
        "rag"
    ]

    answer_lower = answer.lower()

    matches = sum(
        1
        for keyword in technical_keywords
        if keyword in answer_lower
    )

    technical_accuracy = min(
        95,
        55 + matches * 5
    )

    # -----------------------------
    # OVERALL
    # -----------------------------

    overall_score = (
        technical_accuracy * 0.40
        + relevance * 0.25
        + completeness * 0.20
        + communication * 0.15
    )

    overall_score = round(
        overall_score,
        1
    )

    if overall_score >= 85:
        feedback = "Excellent technical answer."
    elif overall_score >= 70:
        feedback = "Good answer. Add more technical depth."
    elif overall_score >= 50:
        feedback = "Average answer. Improve technical explanation."
    else:
        feedback = "Needs improvement in technical concepts."

    return {
        "technical_accuracy": round(
            technical_accuracy, 1
        ),
        "relevance": round(
            relevance, 1
        ),
        "completeness": round(
            completeness, 1
        ),
        "communication": round(
            communication, 1
        ),
        "overall_score": overall_score,
        "feedback": feedback
    }


def generate_report(questions, answers):

    results = []

    for index, question in enumerate(questions):

        answer = ""

        if index < len(answers):
            answer = answers[index]

        evaluation = evaluate_answer(
            answer,
            question
        )

        results.append({
            "question_number": index + 1,
            "question": question,
            "answer": answer,
            **evaluation
        })

    if not results:
        return {
            "overall_score": 0,
            "technical_accuracy": 0,
            "relevance": 0,
            "completeness": 0,
            "communication": 0,
            "questions": [],
            "recommendations": []
        }

    technical_accuracy = sum(
        r["technical_accuracy"]
        for r in results
    ) / len(results)

    relevance = sum(
        r["relevance"]
        for r in results
    ) / len(results)

    completeness = sum(
        r["completeness"]
        for r in results
    ) / len(results)

    communication = sum(
        r["communication"]
        for r in results
    ) / len(results)

    overall_score = (
        technical_accuracy * 0.40
        + relevance * 0.25
        + completeness * 0.20
        + communication * 0.15
    )

    recommendations = []

    if technical_accuracy < 70:
        recommendations.append(
            "Improve core technical concepts."
        )

    if relevance < 70:
        recommendations.append(
            "Focus directly on the question."
        )

    if completeness < 70:
        recommendations.append(
            "Give more detailed answers and examples."
        )

    if communication < 70:
        recommendations.append(
            "Improve the clarity of your explanations."
        )

    if not recommendations:
        recommendations.append(
            "Continue practising technical questions."
        )

    return {
        "overall_score": round(
            overall_score, 1
        ),
        "technical_accuracy": round(
            technical_accuracy, 1
        ),
        "relevance": round(
            relevance, 1
        ),
        "completeness": round(
            completeness, 1
        ),
        "communication": round(
            communication, 1
        ),
        "questions": results,
        "recommendations": recommendations
    }