let selectedAvatar = null;
let ws = null;
let pc = null;
let localStream = null;

const $ = (id) => document.getElementById(id);
const avatarsEl = $("avatars");
const statusEl = $("status");
const remoteVideo = $("remoteVideo");

function setStatus(s) { statusEl.textContent = s; }

async function refreshAvatars() {
  const r = await fetch("/api/avatars");
  const j = await r.json();
  selectedAvatar = j.selected || null;

  avatarsEl.innerHTML = "";
  for (const a of j.avatars) {
    const div = document.createElement("div");
    div.className = "tile";

    const img = document.createElement("img");
    img.src = a.photo_url;
    div.appendChild(img);

    const info = document.createElement("div");
    info.style.marginTop = "8px";
    info.textContent = `id: ${a.id.slice(0, 8)}...  idle: ${a.idle_ready ? "✅" : "⏳"}`;
    div.appendChild(info);

    const actions = document.createElement("div");
    actions.className = "actions";

    const btnSelect = document.createElement("button");
    btnSelect.textContent = (selectedAvatar === a.id) ? "Selected" : "Select";
    btnSelect.className = "small";
    btnSelect.onclick = async () => {
      await fetch(`/api/avatars/${a.id}/select`, { method: "POST" });
      await refreshAvatars();
    };

    const btnIdle = document.createElement("button");
    btnIdle.textContent = a.idle_ready ? "Idle Ready" : "Build Idle";
    btnIdle.disabled = a.idle_ready;
    btnIdle.onclick = async () => {
      btnIdle.disabled = true;
      btnIdle.textContent = "Building...";
      await fetch(`/api/avatars/${a.id}/build-idle`, { method: "POST" });
      await refreshAvatars();
    };

    actions.appendChild(btnSelect);
    actions.appendChild(btnIdle);
    div.appendChild(actions);

    avatarsEl.appendChild(div);
  }
}

async function uploadAvatar() {
  const file = $("file").files?.[0];
  if (!file) return alert("Select an image first.");
  const fd = new FormData();
  fd.append("file", file);
  await fetch("/api/avatars/upload", { method: "POST", body: fd });
  await refreshAvatars();
}

async function startCall() {
  if (!selectedAvatar) return alert("Select an avatar first.");
  setStatus("Connecting...");

  ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws/realtime?avatar_id=${selectedAvatar}`);

  pc = new RTCPeerConnection({
    iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
  });

  pc.ontrack = (ev) => {
    const [stream] = ev.streams;
    remoteVideo.srcObject = stream;
  };

  pc.onicecandidate = (ev) => {
    if (ev.candidate && ws?.readyState === 1) {
      ws.send(JSON.stringify({ type: "candidate", candidate: ev.candidate }));
    }
  };

  localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
  for (const t of localStream.getTracks()) pc.addTrack(t, localStream);

  ws.onmessage = async (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.type === "answer") {
      await pc.setRemoteDescription({ type: msg.sdpType, sdp: msg.sdp });
      setStatus("Live (Speak normally)");
      $("start").disabled = true;
      $("end").disabled = false;
    }
    if (msg.type === "candidate") {
      try { await pc.addIceCandidate(msg.candidate); } catch (e) {}
    }
    if (msg.type === "error") {
      alert(msg.message || "Error");
    }
  };

  ws.onopen = async () => {
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    ws.send(JSON.stringify({ type: "offer", sdp: offer.sdp, sdpType: offer.type }));
  };

  ws.onclose = () => setStatus("Closed");
}

async function endCall() {
  setStatus("Closing...");
  try { localStream?.getTracks()?.forEach(t => t.stop()); } catch {}
  try { pc?.close(); } catch {}
  try { ws?.close(); } catch {}
  pc = null; ws = null; localStream = null;
  remoteVideo.srcObject = null;
  $("start").disabled = false;
  $("end").disabled = true;
  setStatus("Idle");
}

$("upload").onclick = uploadAvatar;
$("refresh").onclick = refreshAvatars;
$("start").onclick = startCall;
$("end").onclick = endCall;

refreshAvatars();
