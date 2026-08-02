"""
facial_analyzer.py
--------------------
Analyzes a recorded answer's video: detects the face in each sampled
frame, checks whether both eyes are visible (a simple proxy for
"looking at the camera" / eye contact), and detects smiles as a
lightweight proxy for positive expression / confidence.

This uses OpenCV's built-in Haar cascades so it runs on CPU with no
extra model downloads. For production-grade emotion recognition,
swap this module out for a deep-learning model (e.g. FER or DeepFace)
without changing the interface the rest of the app relies on.
"""

import cv2

FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
EYE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
SMILE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")


def analyze_video(video_path: str, sample_every_n_frames: int = 5) -> dict:
    """Samples frames from the video and returns eye-contact and
    confidence proxy scores (0-100)."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    total_sampled = 0
    frames_with_face = 0
    frames_with_both_eyes = 0
    frames_with_smile = 0

    frame_index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_index += 1
        if frame_index % sample_every_n_frames != 0:
            continue

        total_sampled += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

        if len(faces) > 0:
            frames_with_face += 1
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])  # largest detected face
            face_gray = gray[y:y + h, x:x + w]

            eyes = EYE_CASCADE.detectMultiScale(face_gray, scaleFactor=1.1, minNeighbors=8)
            if len(eyes) >= 2:
                frames_with_both_eyes += 1

            smiles = SMILE_CASCADE.detectMultiScale(face_gray, scaleFactor=1.7, minNeighbors=22)
            if len(smiles) > 0:
                frames_with_smile += 1

    cap.release()

    if total_sampled == 0:
        return {
            "frames_analyzed": 0,
            "face_detected_ratio": 0.0,
            "eye_contact_score": 0.0,
            "confidence_score": 0.0,
        }

    face_ratio = frames_with_face / total_sampled
    eye_contact_score = (frames_with_both_eyes / total_sampled) * 100
    # Confidence proxy: blend of consistent face presence + a healthy amount of
    # relaxed/positive expression. Weights are heuristic, tune as needed.
    smile_ratio = frames_with_smile / total_sampled
    confidence_score = round(min(100.0, (face_ratio * 60) + (smile_ratio * 40)), 1)

    return {
        "frames_analyzed": total_sampled,
        "face_detected_ratio": round(face_ratio * 100, 1),
        "eye_contact_score": round(eye_contact_score, 1),
        "confidence_score": confidence_score,
    }
