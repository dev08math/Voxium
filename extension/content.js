if (document.getElementById("voxium-root")) {
  const r = document.getElementById("voxium-root");
  r.style.display = r.style.display === "none" ? "block" : "none";
  r.dispatchEvent(new CustomEvent("voxium-refresh"));
} else {
  injectPanel();
}

function injectPanel() {
  const BACKEND = "http://localhost:8000";
  const host = document.createElement("div");
  host.id = "voxium-root";
  host.style.cssText = "position:fixed;top:20px;right:20px;z-index:2147483647;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;";
  document.body.appendChild(host);
  const shadow = host.attachShadow({ mode: "closed" });

  const style = document.createElement("style");
  style.textContent = `
    *{margin:0;padding:0;box-sizing:border-box}
    :host{--bg:#090909;--bg2:#0f0f0f;--border:#1a1a1a;--text:#d0d0d0;--text2:#555;--accent:#00d4aa;--red:#e5484d;--blue:#3b82f6;--mono:"SF Mono","Cascadia Code","Consolas",monospace}

    .panel{width:232px;background:var(--bg);border:1px solid var(--border);border-radius:12px;color:var(--text);font-size:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.5);user-select:none}
    .panel.min .drag,.panel.min .body{display:none}
    .panel.min .pill{display:flex}
    .panel.min{width:auto;border-radius:20px}

    .drag{padding:7px 10px;background:var(--bg2);cursor:grab;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border)}
    .drag:active{cursor:grabbing}
    .logo{font-size:10px;font-weight:700;color:#fff;letter-spacing:.8px;text-transform:uppercase}
    .logo span{color:var(--accent)}
    .tb{display:flex;gap:4px}
    .tb button{background:0;border:0;color:#333;cursor:pointer;font-size:12px;width:18px;height:18px;display:flex;align-items:center;justify-content:center;border-radius:4px;transition:all .12s}
    .tb button:hover{color:#888;background:#1a1a1a}

    .pill{display:none;padding:5px 12px;cursor:pointer;align-items:center;gap:6px;font-size:11px;color:#666}
    .pill .d{width:6px;height:6px;border-radius:50%;background:#333}
    .pill .d.r{background:var(--red);animation:p 1.5s infinite}
    .pill .d.g{background:var(--accent)}

    .body{padding:10px}

    .sr{display:flex;align-items:center;gap:5px;margin-bottom:6px;font-size:11px;color:var(--text2)}
    .d{width:6px;height:6px;border-radius:50%;background:#333;flex-shrink:0}
    .d.r{background:var(--red);animation:p 1.5s infinite}
    .d.b{background:var(--blue);animation:p 1s infinite}
    .d.g{background:var(--accent)}
    @keyframes p{0%,100%{opacity:1}50%{opacity:.3}}

    /* Waveform */
    .wave-wrap{height:40px;margin:4px 0 8px;border-radius:6px;overflow:hidden;background:#0c0c0c;border:1px solid #141414}
    canvas{width:100%;height:100%;display:block}

    .timer{text-align:center;font-size:22px;font-weight:700;font-family:var(--mono);color:#fff;margin:0 0 8px;letter-spacing:1px}
    .timer.dim{color:#222}

    .br{display:flex;gap:4px;margin-bottom:4px}
    .b{flex:1;padding:6px 0;border:1px solid #1a1a1a;border-radius:5px;background:#0d0d0d;color:#666;font-size:10px;font-weight:600;cursor:pointer;text-align:center;transition:all .1s;letter-spacing:.3px}
    .b:hover:not(:disabled){color:#ccc;border-color:#2a2a2a;background:#111}
    .b:disabled{opacity:.2;cursor:not-allowed}
    .b.go{border-color:rgba(0,212,170,.2);color:var(--accent)}
    .b.go:hover:not(:disabled){background:rgba(0,212,170,.06);border-color:rgba(0,212,170,.4)}
    .b.st{border-color:rgba(229,72,77,.2);color:var(--red)}
    .b.st:hover:not(:disabled){background:rgba(229,72,77,.06);border-color:rgba(229,72,77,.4)}
    .b.an{border-color:rgba(59,130,246,.2);color:var(--blue)}
    .b.an:hover:not(:disabled){background:rgba(59,130,246,.06);border-color:rgba(59,130,246,.4)}
    .b.sm{font-size:9px;color:#333;padding:4px 0}

    .warn{font-size:10px;color:#f59e0b;margin-bottom:6px;display:none}

    .cf{display:none;background:#0d0d0d;border:1px solid #1a1a1a;border-radius:6px;padding:8px;margin-top:6px}
    .cf.show{display:block}
    .cf p{font-size:10px;color:#555;margin-bottom:6px;line-height:1.5}

    .v{display:none}.v.a{display:block}
  `;
  shadow.appendChild(style);

  const panel = document.createElement("div");
  panel.className = "panel";
  panel.innerHTML = `
    <div class="pill" id="pill"><span class="d" id="pD"></span><span id="pT">VOX</span></div>
    <div class="drag" id="drag">
      <div class="logo"><span>&#9670;</span> VOXIUM</div>
      <div class="tb">
        <button id="mn" title="Minimize">&#8722;</button>
        <button id="cl" title="Close">&#10005;</button>
      </div>
    </div>
    <div class="body">
      <!-- IDLE -->
      <div class="v a" id="vI">
        <div class="sr"><span class="d"></span>Ready</div>
        <div class="warn" id="wrn"></div>
        <div class="br"><button class="b go" id="bS">START</button></div>
      </div>
      <!-- RECORDING -->
      <div class="v" id="vR">
        <div class="sr"><span class="d r" id="rD"></span><span id="rL">Recording</span></div>
        <div class="wave-wrap"><canvas id="waveCanvas"></canvas></div>
        <div class="timer" id="tm">00:00</div>
        <div class="br">
          <button class="b" id="bP">PAUSE</button>
          <button class="b st" id="bSt">STOP</button>
        </div>
      </div>
      <!-- SAVING -->
      <div class="v" id="vSv">
        <div class="sr"><span class="d b"></span>Saving...</div>
      </div>
      <!-- RECORDED -->
      <div class="v" id="vRd">
        <div class="sr"><span class="d g"></span>Recording saved</div>
        <div class="br"><button class="b an" id="bA">GENERATE INTELLIGENCE</button></div>
        <div class="br"><button class="b sm" id="bN1">DISCARD</button></div>
      </div>
      <!-- ANALYZING -->
      <div class="v" id="vAn">
        <div class="sr"><span class="d b"></span>Analyzing</div>
      </div>
      <!-- COMPLETE -->
      <div class="v" id="vC">
        <div class="sr"><span class="d g"></span>Analysis ready</div>
        <div class="br"><button class="b go" id="bV">VIEW RESULTS</button></div>
        <div class="br"><button class="b sm" id="bN2">NEW RECORDING</button></div>
      </div>
      <!-- ERROR -->
      <div class="v" id="vE">
        <div class="sr"><span class="d"></span>Error</div>
        <div style="font-size:9px;color:#444;margin-bottom:4px" id="eM"></div>
        <div class="br"><button class="b sm" id="bN3">RETRY</button></div>
      </div>
      <!-- CONFIRM -->
      <div class="cf" id="cf">
        <p>Discard current recording?</p>
        <div class="br">
          <button class="b st" id="cY">DISCARD</button>
          <button class="b" id="cN">CANCEL</button>
        </div>
      </div>
    </div>
  `;
  shadow.appendChild(panel);

  const $ = (id) => shadow.getElementById(id);
  const vs = {idle:$("vI"),recording:$("vR"),saving:$("vSv"),recorded:$("vRd"),analyzing:$("vAn"),complete:$("vC"),error:$("vE")};
  let poll = null, meetingId = null;

  function sv(n){Object.values(vs).forEach(v=>v.classList.remove("a"));vs[n]?.classList.add("a");$("cf").classList.remove("show");$("wrn").style.display="none";}
  function fmt(ms){const s=Math.floor(ms/1000);return `${String(Math.floor(s/60)).padStart(2,"0")}:${String(s%60).padStart(2,"0")}`;}
  function sp(){stopP();poll=setInterval(fs,800);}
  function stopP(){if(poll){clearInterval(poll);poll=null;}}

  async function fs(){try{const s=await chrome.runtime.sendMessage({type:"get-tab-state"});as(s);}catch(e){}}

  function as(s){
    if(!s){sv("idle");return;}
    const st=s.status||"idle";
    $("pD").className="d";$("pT").textContent="VOX";
    if(st==="recording"){$("pD").classList.add("r");$("pT").textContent=fmt(s.elapsed||0);}
    else if(st==="analyzing"||st==="saving")$("pD").classList.add("b");
    else if(st==="complete"||st==="recorded")$("pD").classList.add("g");
    if(s.meetingId)meetingId=s.meetingId;

    switch(st){
      case"idle":sv("idle");stopP();stopWave();break;
      case"recording":sv("recording");$("rD").className="d r";$("rL").textContent="Recording";$("bP").textContent="PAUSE";$("tm").textContent=fmt(s.elapsed||0);$("tm").classList.remove("dim");startWave();break;
      case"paused":sv("recording");$("rD").className="d";$("rL").textContent="Paused";$("bP").textContent="RESUME";$("tm").textContent=fmt(s.elapsed||0);$("tm").classList.add("dim");stopWave();break;
      case"saving":sv("saving");stopWave();break;
      case"recorded":sv("recorded");stopP();stopWave();break;
      case"analyzing":sv("analyzing");break;
      case"complete":sv("complete");stopP();stopWave();break;
      case"error":sv("error");$("eM").textContent=s.error||"";stopP();stopWave();break;
    }
  }

  // ── Waveform ──
  let waveAnim = null;
  const canvas = $("waveCanvas");
  const ctx = canvas.getContext("2d");

  function startWave(){
    stopWave();
    const w = canvas.offsetWidth; const h = canvas.offsetHeight;
    canvas.width = w * 2; canvas.height = h * 2;
    ctx.scale(2, 2);
    const bars = 32;
    const barW = w / bars - 1;
    let phase = 0;

    function draw(){
      ctx.clearRect(0, 0, w, h);
      const mid = h / 2;
      for(let i = 0; i < bars; i++){
        const amp = (Math.sin(phase + i * 0.3) * 0.3 + 0.4 + Math.random() * 0.2) * mid * 0.7;
        const x = i * (barW + 1);
        ctx.fillStyle = `rgba(0, 212, 170, ${0.25 + amp / mid * 0.5})`;
        ctx.fillRect(x, mid - amp, barW, amp * 2);
      }
      phase += 0.08;
      waveAnim = requestAnimationFrame(draw);
    }
    draw();
  }

  function stopWave(){
    if(waveAnim){cancelAnimationFrame(waveAnim);waveAnim=null;}
    if(ctx && canvas.width > 0){
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }

  // ── Drag ──
  let dg=false,dx=0,dy=0;
  function ds(e){dg=true;dx=e.clientX-host.offsetLeft;dy=e.clientY-host.offsetTop;e.target.setPointerCapture(e.pointerId);}
  function dm(e){if(!dg)return;host.style.left=(e.clientX-dx)+"px";host.style.top=(e.clientY-dy)+"px";host.style.right="auto";}
  function de(){dg=false;}
  $("drag").addEventListener("pointerdown",ds);$("drag").addEventListener("pointermove",dm);$("drag").addEventListener("pointerup",de);
  $("pill").addEventListener("pointerdown",ds);$("pill").addEventListener("pointermove",dm);$("pill").addEventListener("pointerup",de);

  $("mn").addEventListener("click",e=>{e.stopPropagation();panel.classList.add("min");});
  $("pill").addEventListener("click",()=>{if(!dg)panel.classList.remove("min");});
  $("cl").addEventListener("click",e=>{e.stopPropagation();host.style.display="none";});

  // ── Buttons ──
  $("bS").addEventListener("click",async()=>{
    const ck=await chrome.runtime.sendMessage({type:"is-recording-active"});
    if(ck.active){$("wrn").textContent="Recording active on another tab";$("wrn").style.display="block";return;}
    const r=await chrome.runtime.sendMessage({type:"start-recording"});
    if(r.success){as({status:"recording",elapsed:0});sp();}
    else as({status:"error",error:r.error});
  });

  $("bP").addEventListener("click",async()=>{
    const s=await chrome.runtime.sendMessage({type:"get-tab-state"});
    if(s.status==="recording")await chrome.runtime.sendMessage({type:"pause-recording"});
    else if(s.status==="paused")await chrome.runtime.sendMessage({type:"resume-recording"});
    fs();
  });

  $("bSt").addEventListener("click",async()=>{
    await chrome.runtime.sendMessage({type:"stop-recording"});
    as({status:"saving"});sp();
  });

  $("bA").addEventListener("click",async()=>{
    const s=await chrome.runtime.sendMessage({type:"get-tab-state"});
    if(s.status==="analyzing")return;
    const r=await chrome.runtime.sendMessage({type:"analyze"});
    if(r.success){meetingId=r.meetingId;as({status:"analyzing"});sp();}
  });

  $("bV").addEventListener("click",()=>{
    if(meetingId)window.open(`${BACKEND}/meeting/${meetingId}`,"_blank");
  });

  function sc(){$("cf").classList.add("show");}
  $("bN1").addEventListener("click",sc);
  $("bN2").addEventListener("click",sc);
  $("bN3").addEventListener("click",async()=>{await chrome.runtime.sendMessage({type:"discard-recording"});as({status:"idle"});});
  $("cY").addEventListener("click",async()=>{await chrome.runtime.sendMessage({type:"discard-recording"});$("cf").classList.remove("show");as({status:"idle"});});
  $("cN").addEventListener("click",()=>$("cf").classList.remove("show"));

  chrome.storage.onChanged.addListener(c=>{if(c.tabStates)fs();});
  host.addEventListener("voxium-refresh",()=>{fs();sp();});
  fs();sp();
}