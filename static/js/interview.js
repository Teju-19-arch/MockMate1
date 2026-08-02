/* MockMate live interview room
   Handles: AI avatar speaking questions (Web Speech API), live webcam/mic
   capture (MediaRecorder), uploading the recorded answer for analysis,
   and rendering the returned scores/feedback. */

(function () {
  const questions = window.MOCKMATE_QUESTIONS || [];
  const sessionId = window.MOCKMATE_SESSION_ID;
  let qIndex = 0;
  let mediaStream = null;
  let mediaRecorder = null;
  let recordedChunks = [];

  const avatarPanel = document.getElementById('avatar-panel');
  const avatarStatus = document.getElementById('avatar-status');
  const questionIndexEl = document.getElementById('question-index');
  const questionTextEl = document.getElementById('question-text');
  const trackFill = document.getElementById('track-fill');
  const trackLabel = document.getElementById('track-label');

  const videoEl = document.getElementById('live-video');
  const recIndicator = document.getElementById('rec-indicator');

  const btnCamera = document.getElementById('btn-camera');
  const btnRecord = document.getElementById('btn-record');
  const btnStop = document.getElementById('btn-stop');
  const btnReplay = document.getElementById('btn-replay');
  const btnNext = document.getElementById('btn-next');
  const btnFinish = document.getElementById('btn-finish');

  const resultPanel = document.getElementById('result-panel');
  const analyzingMsg = document.getElementById('analyzing-msg');
  const resultContent = document.getElementById('result-content');

  function updateProgress() {
    const pct = Math.round((qIndex / questions.length) * 100);
    trackFill.style.width = pct + '%';
    trackLabel.textContent = `Question ${Math.min(qIndex + 1, questions.length)} of ${questions.length}`;
    questionIndexEl.textContent = `QUESTION ${qIndex + 1} OF ${questions.length}`;
  }

  function speakQuestion(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.98;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      avatarPanel.classList.add('speaking');
      avatarStatus.textContent = 'SPEAKING';
    };
    utterance.onend = () => {
      avatarPanel.classList.remove('speaking');
      avatarStatus.textContent = 'LISTENING';
    };
    window.speechSynthesis.speak(utterance);
  }

  function loadQuestion(index) {
    if (index >= questions.length) {
      showCompletion();
      return;
    }
    questionTextEl.textContent = questions[index];
    updateProgress();
    resultPanel.classList.remove('visible');
    resultContent.style.display = 'none';
    analyzingMsg.style.display = 'none';
    btnNext.style.display = 'none';
    btnRecord.style.display = 'inline-flex';
    btnStop.style.display = 'none';
    speakQuestion(questions[index]);
  }

  function showCompletion() {
    questionTextEl.textContent = 'Interview complete -- great work!';
    avatarStatus.textContent = 'DONE';
    document.querySelector('.control-row').style.display = 'none';
    btnFinish.style.display = 'inline-flex';
    trackFill.style.width = '100%';
    trackLabel.textContent = `All ${questions.length} questions completed`;
  }

  // ---- Camera / mic setup ----
  btnCamera.addEventListener('click', async () => {
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      videoEl.srcObject = mediaStream;
      btnCamera.disabled = true;
      btnCamera.textContent = 'Camera active';
      btnRecord.disabled = false;
      avatarStatus.textContent = 'LISTENING';
    } catch (err) {
      alert('Could not access camera/microphone. Please allow permissions and try again.\n\n' + err.message);
    }
  });

  // ---- Recording ----
  btnRecord.addEventListener('click', () => {
    if (!mediaStream) return;
    recordedChunks = [];
    const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp8,opus')
      ? 'video/webm;codecs=vp8,opus' : 'video/webm';
    mediaRecorder = new MediaRecorder(mediaStream, { mimeType });

    mediaRecorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) recordedChunks.push(e.data);
    };
    mediaRecorder.onstop = handleRecordingStop;

    mediaRecorder.start();
    recIndicator.classList.add('active');
    btnRecord.style.display = 'none';
    btnStop.style.display = 'inline-flex';
  });

  btnStop.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    recIndicator.classList.remove('active');
    btnStop.style.display = 'none';
  });

  btnReplay.addEventListener('click', () => {
    speakQuestion(questions[qIndex]);
  });

  async function handleRecordingStop() {
    const blob = new Blob(recordedChunks, { type: 'video/webm' });

    resultPanel.classList.add('visible');
    analyzingMsg.style.display = 'block';
    resultContent.style.display = 'none';

    const formData = new FormData();
    formData.append('media', blob, 'answer.webm');
    formData.append('question', questions[qIndex]);

    try {
      const response = await fetch(`/api/analyze/${sessionId}`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();

      analyzingMsg.style.display = 'none';

      if (data.error) {
        resultContent.style.display = 'block';
        document.getElementById('feedback-text').textContent =
          'Analysis error: ' + data.error + ' -- you can still move to the next question.';
      } else {
        resultContent.style.display = 'block';
        document.getElementById('score-overall').textContent = data.overall_score;
        document.getElementById('score-eye').textContent = data.eye_contact_score + '%';
        document.getElementById('score-conf').textContent = data.confidence_score;
        document.getElementById('score-filler').textContent = data.filler_word_count;
        document.getElementById('score-wpm').textContent = data.speaking_rate_wpm;
        document.getElementById('feedback-text').textContent = data.feedback;
        document.getElementById('transcript-text').textContent = data.transcript
          ? `"${data.transcript}"` : '(no speech detected in the recording)';
      }
      btnNext.style.display = 'inline-flex';
    } catch (err) {
      analyzingMsg.style.display = 'none';
      resultContent.style.display = 'block';
      document.getElementById('feedback-text').textContent = 'Could not reach the server for analysis: ' + err.message;
      btnNext.style.display = 'inline-flex';
    }
  }

  btnNext.addEventListener('click', () => {
    qIndex += 1;
    loadQuestion(qIndex);
  });

  // ---- Init ----
  updateProgress();
  if (questions.length > 0) {
    speakQuestion(questions[0]);
  }
})();
