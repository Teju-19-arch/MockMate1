/* MockMate live interview room
   Handles: AI avatar speaking questions (Web Speech API), live webcam/mic
   capture (MediaRecorder), uploading the recorded answer for analysis
   in the background, and -- once every question is answered --
   redirecting to a single overall results page (no per-question scores
   shown during the interview itself). */

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

  const resultPanel = document.getElementById('result-panel');
  const analyzingMsg = document.getElementById('analyzing-msg');
  const resultContent = document.getElementById('result-content');
  const feedbackText = document.getElementById('feedback-text');

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

  const isLastQuestion = () => qIndex + 1 >= questions.length;

  async function handleRecordingStop() {
    const blob = new Blob(recordedChunks, { type: 'video/webm' });

    resultPanel.classList.add('visible');
    analyzingMsg.style.display = 'block';
    resultContent.style.display = 'none';
    analyzingMsg.textContent = isLastQuestion()
      ? 'Analyzing your final answer and preparing your overall report...'
      : 'Analyzing your speech and expressions...';

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

      if (isLastQuestion()) {
        window.location.href = `/interview/${sessionId}/results`;
        return;
      }

      resultContent.style.display = 'block';
      if (data.error) {
        feedbackText.textContent = 'Analysis error: ' + data.error + ' -- you can still move to the next question.';
      } else {
        feedbackText.textContent = '✓ Answer recorded.';
      }
      btnNext.style.display = 'inline-flex';
    } catch (err) {
      analyzingMsg.style.display = 'none';
      if (isLastQuestion()) {
        window.location.href = `/interview/${sessionId}/results`;
        return;
      }
      resultContent.style.display = 'block';
      feedbackText.textContent = 'Could not reach the server for analysis: ' + err.message;
      btnNext.style.display = 'inline-flex';
    }
  }

  btnNext.addEventListener('click', () => {
    qIndex += 1;
    loadQuestion(qIndex);
  });

  updateProgress();
  if (questions.length > 0) {
    speakQuestion(questions[0]);
  }
})();