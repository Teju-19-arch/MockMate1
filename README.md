# MockMate — Flask Edition (Live Interview + AI Avatar)

A full rebuild of MockMate as a real website: **live webcam/mic recording**
(no more file uploads), an **animated AI avatar** ("Aria") that speaks each
question aloud, and a **placement-focused dashboard** covering both
job-description-based prep and company-wise campus placement drives.

## What's new vs. the Streamlit version

| Feature | Streamlit version | This version |
|---|---|---|
| Recording | Upload pre-recorded audio/video files | **Live in-browser webcam + mic recording** via MediaRecorder |
| Question delivery | Text only | **AI avatar speaks questions aloud** (Web Speech API) with animated waveform |
| Interview modes | Domain only | **Domain / Company placement drive / Job description** |
| Company prep | None | **TCS, Infosys, Wipro, Accenture, Amazon, Google, Microsoft** — real aptitude + technical + HR round questions |
| Job-specific prep | None | Paste a JD → auto-extracts role, skills, generates tailored questions |
| Dashboard | Basic table + line chart | Placement readiness score, per-company readiness chips, styled history table |
| Visual design | Default Streamlit theme | Custom navy/brass "interview panel" design system |

## Project structure
```
mockmate_flask/
├── app.py                      # Flask routes: auth, dashboard, interview setup, live analysis API
├── database.py                  # SQLite: users, sessions (mode-aware), reports
├── requirements.txt
├── modules/
│   ├── resume_parser.py         # PDF/DOCX text + skill extraction (unchanged from v1)
│   ├── job_parser.py            # NEW: extracts role + skills from a pasted job description
│   ├── question_bank.py         # Expanded: HR + technical + company-wise placement banks
│   ├── question_generator.py    # NEW: builds questions for domain / company / job modes
│   ├── speech_analyzer.py       # Transcription, filler words, pauses, WPM (unchanged)
│   ├── facial_analyzer.py       # OpenCV eye-contact/confidence scoring (unchanged)
│   └── report_generator.py      # Combines speech + facial into one score + feedback
├── static/
│   ├── css/style.css            # Full design system (see below)
│   └── js/interview.js          # Avatar TTS + live recording + upload/analyze flow
└── templates/
    ├── base.html, login.html, register.html
    ├── dashboard.html            # Readiness score, company chips, history
    ├── new_interview.html        # Mode picker: domain / company / job
    └── interview_room.html       # The live avatar + webcam interview screen
```

## Design system
Built around the subject itself — formal Indian campus/job placement interviews:
- **Colors:** ink navy `#1B2340`, brass `#C9A227`, paper `#F7F5F0`, sage `#3E7C6F` (success), coral `#E4572E` (alerts)
- **Type:** Fraunces (serif display, for headlines), Inter (body/UI), IBM Plex Mono (scores, timers)
- **Signature element:** the avatar sits in a circular "panel window" with a live waveform that animates while it talks — a direct visual echo of a real interview panel

## Setup

1. **Install Python 3.10+** and **ffmpeg** (same as before — needed by `pydub`/OpenCV for reading the recorded `.webm` files):
   - Windows: download from ffmpeg.org, add `bin` to PATH
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

2. From inside the `mockmate_flask` folder:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac/Linux

   pip install -r requirements.txt
   ```

3. Run it:
   ```bash
   python app.py
   ```
   Open **http://localhost:5000** in your browser.

4. **Important — camera/mic permissions:** browsers only allow camera/mic
   access on `localhost` or over HTTPS. Running on `localhost:5000` (as
   above) works fine for your local demo/viva. If you ever deploy this to
   a real domain, you'll need HTTPS for the recording to work.

## How the live interview flow works

1. **New Interview** → pick a mode:
   - **General Domain** — AIML / Web Development / Data Science / HR
   - **Campus Placement** — pick a company (TCS, Infosys, Wipro, Accenture,
     Amazon, Google, Microsoft) → pulls that company's real aptitude +
     technical + HR round questions
   - **Job Description** — paste a JD → MockMate extracts the role and
     required skills and builds tailored questions
   - Optionally upload a resume → adds 2-3 resume-specific questions
2. You land in the **live interview room**:
   - The avatar "Aria" speaks the question aloud automatically
   - Click **Enable camera & mic** (browser will ask permission)
   - Click **Start recording answer**, answer out loud, click **Stop & analyze**
   - Your recording is analyzed (transcript, filler words, pace, pauses,
     eye contact, confidence) and scored — nothing is saved to disk beyond
     the extracted scores; the raw recording is deleted right after analysis
   - Click **Next question** to continue, or **Replay question** to hear it again
3. **Dashboard** shows your overall placement readiness score, average
   eye contact, per-company readiness (once you've done company-specific
   sessions), and a history table of every answer.

## Known limitations / good next steps for your submission

- **Speech transcription** uses Google's free Web Speech API via
  `SpeechRecognition`, which needs live internet access at analysis time.
  For offline/more accurate transcription, swap in `openai-whisper`.
- **Facial analysis** still uses OpenCV Haar cascades (fast, CPU-only,
  no extra downloads). For a stronger accuracy claim in your report,
  swap the internals of `modules/facial_analyzer.py` for `FER` or
  `DeepFace` — the function signature is unchanged so nothing else breaks.
- **Avatar voice** currently uses the browser's built-in Web Speech API
  (works offline, but voice quality depends on the browser/OS). For a more
  "human" sounding avatar, you could route question text through a
  cloud TTS API (e.g. ElevenLabs, Google Cloud TTS) instead.
- **Question generation** is template + keyword based. You can extend
  `question_generator.py` / `job_parser.py` to call an LLM API for more
  dynamic, deeply tailored phrasing.
- Company bank currently has a handful of sample questions per round per
  company — easy to expand by adding more entries to
  `modules/question_bank.py`'s `COMPANY_QUESTION_BANK` dict.

## Tested end-to-end before delivery

- Registration, login, and session auth
- All three question-generation modes (domain / company / job description)
- The full live-analysis pipeline: a synthetic recorded `.webm` file was
  uploaded through `/api/analyze/<session_id>` and correctly produced
  transcript/score/feedback JSON, which was saved to the database
- Dashboard correctly reflects saved reports (readiness score, history table)
- The Flask app boots and serves all pages (login, register, dashboard,
  new-interview, interview-room) without errors
