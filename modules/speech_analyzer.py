"""
speech_analyzer.py
--------------------
Analyzes a recorded answer's audio: transcribes speech, counts filler
words, detects pauses (silence gaps), and estimates speaking rate (WPM).

Requires ffmpeg installed on the host machine (used by pydub for
reading non-WAV formats such as mp3/m4a).
"""

import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import detect_silence

FILLER_WORDS = ["um", "uh", "like", "you know", "actually", "basically", "so yeah", "i mean"]


def transcribe_audio(audio_path: str) -> str:
    """Convert the audio file to WAV (if needed) and transcribe using
    the SpeechRecognition Google Web Speech API (requires internet)."""
    wav_path = _ensure_wav(audio_path)
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"[speech recognition service error: {e}]"


def _ensure_wav(audio_path: str) -> str:
    if audio_path.lower().endswith(".wav"):
        return audio_path
    audio = AudioSegment.from_file(audio_path)
    wav_path = audio_path.rsplit(".", 1)[0] + "_converted.wav"
    audio.export(wav_path, format="wav")
    return wav_path


def count_filler_words(transcript: str) -> int:
    text = transcript.lower()
    return sum(text.count(word) for word in FILLER_WORDS)


def count_pauses(audio_path: str, silence_thresh_db=-40, min_silence_len_ms=700) -> int:
    """Counts silence gaps longer than min_silence_len_ms -- a proxy for
    hesitation / awkward pausing during the answer."""
    wav_path = _ensure_wav(audio_path)
    audio = AudioSegment.from_wav(wav_path)
    silent_ranges = detect_silence(
        audio, min_silence_len=min_silence_len_ms, silence_thresh=silence_thresh_db
    )
    return len(silent_ranges)


def speaking_rate_wpm(transcript: str, audio_duration_seconds: float) -> float:
    if audio_duration_seconds <= 0:
        return 0.0
    word_count = len(transcript.split())
    minutes = audio_duration_seconds / 60.0
    return round(word_count / minutes, 1) if minutes > 0 else 0.0


def analyze_speech(audio_path: str) -> dict:
    """Full speech analysis pipeline used by report_generator.py"""
    wav_path = _ensure_wav(audio_path)
    audio = AudioSegment.from_wav(wav_path)
    duration_seconds = len(audio) / 1000.0

    transcript = transcribe_audio(audio_path)
    filler_count = count_filler_words(transcript)
    pauses = count_pauses(audio_path)
    wpm = speaking_rate_wpm(transcript, duration_seconds)

    return {
        "transcript": transcript,
        "duration_seconds": round(duration_seconds, 1),
        "filler_word_count": filler_count,
        "pause_count": pauses,
        "speaking_rate_wpm": wpm,
    }
