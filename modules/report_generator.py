"""
report_generator.py
----------------------
Combines speech_analyzer + facial_analyzer output into one performance
report per answer, with a composite overall_score and human-readable
feedback / improvement suggestions.
"""

IDEAL_WPM_RANGE = (110, 160)  # comfortable speaking pace for interviews


def _speech_component_score(speech: dict) -> float:
    score = 100.0

    # Penalize filler words
    score -= min(30, speech.get("filler_word_count", 0) * 4)

    # Penalize excessive pauses
    score -= min(20, speech.get("pause_count", 0) * 3)

    # Penalize speaking pace outside the ideal range
    wpm = speech.get("speaking_rate_wpm", 0)
    low, high = IDEAL_WPM_RANGE
    if wpm and wpm < low:
        score -= min(20, (low - wpm) * 0.5)
    elif wpm and wpm > high:
        score -= min(20, (wpm - high) * 0.5)

    return max(0.0, round(score, 1))


def _build_feedback(speech: dict, facial: dict, speech_score: float) -> str:
    tips = []

    if speech.get("filler_word_count", 0) > 3:
        tips.append("Try to reduce filler words like 'um', 'uh', and 'like' -- pause silently instead.")
    if speech.get("pause_count", 0) > 4:
        tips.append("You paused frequently; practicing answers out loud can help you speak more fluidly.")

    wpm = speech.get("speaking_rate_wpm", 0)
    low, high = IDEAL_WPM_RANGE
    if wpm and wpm < low:
        tips.append("Your speaking pace was a bit slow -- try to sound more energetic and engaged.")
    elif wpm and wpm > high:
        tips.append("You spoke quite fast -- slowing down slightly will make your answers easier to follow.")

    if facial.get("eye_contact_score", 0) < 50:
        tips.append("Try to look at the camera more consistently to simulate stronger eye contact.")
    if facial.get("confidence_score", 0) < 50:
        tips.append("Sit centered in frame with good lighting, and relax your expression to project more confidence.")

    if not tips:
        tips.append("Great job! Your pacing, filler-word usage, and eye contact were all in a strong range.")

    return " ".join(tips)


def build_report(speech: dict, facial: dict) -> dict:
    """speech = output of speech_analyzer.analyze_speech()
       facial = output of facial_analyzer.analyze_video()
       Returns the combined dict that database.save_report() expects."""
    speech_score = _speech_component_score(speech)
    facial_score = facial.get("confidence_score", 0.0)

    # Weighted overall score: 55% verbal delivery, 45% non-verbal presence
    overall_score = round((speech_score * 0.55) + (facial_score * 0.45), 1)

    feedback = _build_feedback(speech, facial, speech_score)

    return {
        "transcript": speech.get("transcript", ""),
        "filler_word_count": speech.get("filler_word_count", 0),
        "speaking_rate_wpm": speech.get("speaking_rate_wpm", 0.0),
        "pause_count": speech.get("pause_count", 0),
        "eye_contact_score": facial.get("eye_contact_score", 0.0),
        "confidence_score": facial_score,
        "overall_score": overall_score,
        "feedback": feedback,
    }
