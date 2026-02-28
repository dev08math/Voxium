const BACKEND_URL = "http://localhost:8000";
let activeRecording = null;

async function getTabState(tabId) {
  const data = await chrome.storage.local.get("tabStates");
  return data.tabStates?.[String(tabId)] || { status: "idle" };
}

async function setTabState(tabId, update) {
  const data = await chrome.storage.local.get("tabStates");
  const states = data.tabStates || {};
  states[String(tabId)] = { ...(states[String(tabId)] || {}), ...update };
  await chrome.storage.local.set({ tabStates: states });
}

async function clearTabState(tabId) {
  const data = await chrome.storage.local.get("tabStates");
  const states = data.tabStates || {};
  delete states[String(tabId)];
  await chrome.storage.local.set({ tabStates: states });
}

async function ensureOffscreenDocument() {
  const contexts = await chrome.runtime.getContexts({ contextTypes: ["OFFSCREEN_DOCUMENT"] });
  if (contexts.length > 0) return;
  await chrome.offscreen.createDocument({
    url: "offscreen.html",
    reasons: ["USER_MEDIA"],
    justification: "Recording tab audio",
  });
}

chrome.action.onClicked.addListener(async (tab) => {
  try {
    await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["content.js"] });
  } catch (e) { console.error("Inject failed:", e); }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender).then(sendResponse);
  return true;
});

async function handleMessage(message, sender) {
  const tabId = message.tabId || sender.tab?.id;

  switch (message.type) {
    case "get-tab-state": {
      const state = await getTabState(tabId);
      let elapsed = 0;
      if (activeRecording && activeRecording.tabId === tabId) {
        elapsed = Date.now() - activeRecording.startTime - activeRecording.pausedDuration;
        if (activeRecording.pauseStart) elapsed -= Date.now() - activeRecording.pauseStart;
      }
      return { ...state, elapsed };
    }

    case "is-recording-active":
      return { active: activeRecording !== null };

    case "start-recording": {
      if (activeRecording) return { success: false, error: "Recording active on another tab" };
      try {
        const streamId = await chrome.tabCapture.getMediaStreamId({ targetTabId: tabId });
        await ensureOffscreenDocument();
        chrome.runtime.sendMessage({ type: "offscreen-start-recording", streamId });
        activeRecording = { tabId, startTime: Date.now(), pausedDuration: 0, pauseStart: null };
        await setTabState(tabId, { status: "recording" });
        return { success: true };
      } catch (e) { return { success: false, error: e.message }; }
    }

    case "pause-recording":
      chrome.runtime.sendMessage({ type: "offscreen-pause-recording" });
      if (activeRecording) activeRecording.pauseStart = Date.now();
      await setTabState(tabId, { status: "paused" });
      return { success: true };

    case "resume-recording":
      chrome.runtime.sendMessage({ type: "offscreen-resume-recording" });
      if (activeRecording?.pauseStart) {
        activeRecording.pausedDuration += Date.now() - activeRecording.pauseStart;
        activeRecording.pauseStart = null;
      }
      await setTabState(tabId, { status: "recording" });
      return { success: true };

    case "stop-recording":
      chrome.runtime.sendMessage({ type: "offscreen-stop-recording" });
      await setTabState(tabId, { status: "saving" });
      return { success: true };

    case "analyze": {
      const state = await getTabState(tabId);
      if (!state.meetingId) return { success: false, error: "No recording" };
      if (state.status === "analyzing") return { success: false, error: "Already analyzing" };
      await setTabState(tabId, { status: "analyzing" });
      try {
        await fetch(`${BACKEND_URL}/api/meeting/${state.meetingId}/analyze`, { method: "POST" });
        pollForCompletion(tabId, state.meetingId);
        return { success: true, meetingId: state.meetingId };
      } catch (e) {
        await setTabState(tabId, { status: "error", error: e.message });
        return { success: false, error: e.message };
      }
    }

    case "discard-recording":
      await clearTabState(tabId);
      activeRecording = null;
      return { success: true };

    case "upload-complete": {
      const recTabId = activeRecording?.tabId;
      activeRecording = null;
      if (recTabId) await setTabState(recTabId, { meetingId: message.meetingId, status: "recorded" });
      return {};
    }

    case "upload-error": {
      const recTabId = activeRecording?.tabId;
      activeRecording = null;
      if (recTabId) await setTabState(recTabId, { status: "error", error: message.error });
      return {};
    }
  }
  return {};
}

function pollForCompletion(tabId, meetingId) {
  const poll = async () => {
    try {
      const resp = await fetch(`${BACKEND_URL}/api/meeting/${meetingId}/status`);
      const data = await resp.json();
      if (data.status === "complete") await setTabState(tabId, { status: "complete" });
      else if (data.status === "error") await setTabState(tabId, { status: "error", error: data.error });
      else setTimeout(poll, 2000);
    } catch (e) { setTimeout(poll, 3000); }
  };
  poll();
}