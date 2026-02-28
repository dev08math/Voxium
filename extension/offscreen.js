let mediaRecorder = null;
let recordedChunks = [];
let mediaStream = null;
let audioPlayback = null;

const BACKEND_URL = "http://localhost:8000";

chrome.runtime.onMessage.addListener((message) => {
  switch (message.type) {
    case "offscreen-start-recording": startRecording(message.streamId); break;
    case "offscreen-pause-recording": if (mediaRecorder?.state === "recording") mediaRecorder.pause(); break;
    case "offscreen-resume-recording": if (mediaRecorder?.state === "paused") mediaRecorder.resume(); break;
    case "offscreen-stop-recording": stopRecording(); break;
  }
});

async function startRecording(streamId) {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: { mandatory: { chromeMediaSource: "tab", chromeMediaSourceId: streamId } },
    });

    audioPlayback = new Audio();
    audioPlayback.srcObject = new MediaStream(mediaStream.getAudioTracks());
    audioPlayback.play().catch(() => {});

    recordedChunks = [];
    const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
      ? "audio/webm;codecs=opus" : "audio/ogg;codecs=opus";

    mediaRecorder = new MediaRecorder(mediaStream, { mimeType });
    mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) recordedChunks.push(e.data); };
    mediaRecorder.onstop = async () => {
      const blob = new Blob(recordedChunks, { type: mediaRecorder.mimeType });
      await upload(blob);
      cleanup();
    };
    mediaRecorder.onerror = () => cleanup();
    mediaRecorder.start(1000);
  } catch (err) {
    console.error("Start failed:", err);
  }
}

async function upload(blob) {
  try {
    const form = new FormData();
    form.append("file", blob, "recording.webm");
    const resp = await fetch(`${BACKEND_URL}/api/upload`, { method: "POST", body: form });
    const data = await resp.json();
    chrome.runtime.sendMessage({ type: "upload-complete", meetingId: data.meeting_id });
  } catch (err) {
    chrome.runtime.sendMessage({ type: "upload-error", error: err.message });
  }
}

function stopRecording() {
  if (mediaRecorder?.state !== "inactive") mediaRecorder.stop();
  else cleanup();
}

function cleanup() {
  if (audioPlayback) { audioPlayback.pause(); audioPlayback.srcObject = null; audioPlayback = null; }
  mediaStream?.getTracks().forEach((t) => t.stop());
  mediaStream = null; mediaRecorder = null; recordedChunks = [];
}