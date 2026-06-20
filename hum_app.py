#!/usr/bin/env python3
"""Hum Studio — record/hum an idea, get a clean in-key instrument part.

Local web app over the hum2inst engine: record a hum (or upload a clip),
pick tempo/key/instrument, and get back a MIDI part + an audio preview you can
hear. Reused by hum_desktop.py as a native window.

  pip install -r hum2inst/requirements.txt flask
  brew install ffmpeg
  python hum_app.py            # → http://127.0.0.1:5005
"""
from __future__ import annotations
import os
import subprocess
import uuid
from flask import Flask, request, jsonify, send_from_directory, Response

from hum2inst import run, render, INSTRUMENTS, HumError

ROOT = os.path.dirname(os.path.abspath(__file__))
HUM = os.path.join(ROOT, "out", "hum")
os.makedirs(HUM, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024


def _to_wav(src: str, dst: str) -> None:
    """Convert any recorded/uploaded clip to mono 44.1k WAV (basic-pitch friendly)."""
    if not _have("ffmpeg"):
        raise HumError("ffmpeg not found. Install it: brew install ffmpeg")
    p = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", src,
                        "-ac", "1", "-ar", "44100", dst],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise HumError(f"couldn't read that audio:\n{p.stderr[-300:]}")


def _have(binname: str) -> bool:
    from shutil import which
    return which(binname) is not None


@app.get("/")
def index():
    return Response(INDEX, mimetype="text/html")


@app.post("/api/hum")
def api_hum():
    f = request.files.get("audio")
    if not f or not f.filename:
        return jsonify(ok=False, error="No audio — record or choose a clip first."), 400
    uid = uuid.uuid4().hex[:8]
    raw = os.path.join(HUM, f"{uid}_raw")
    f.save(raw)
    wav = os.path.join(HUM, f"{uid}.wav")
    midi = os.path.join(HUM, f"{uid}.mid")
    prev = os.path.join(HUM, f"{uid}_preview.wav")
    try:
        _to_wav(raw, wav)
        bpm = float(request.form.get("bpm", 90))
        key = request.form.get("key", "Cmaj")
        grid = int(request.form.get("grid", 16))
        inst = request.form.get("instrument", "bass")
        faithful = request.form.get("faithful") == "1"
        res, pm = run(wav, midi, bpm=bpm, key=key, grid=grid,
                      correct=not faithful, monophonic=True)
        if res.notes == 0:
            return jsonify(ok=False, error="No notes detected — try humming a clear, steady tone."), 400
        render(pm, prev, instrument=inst)
    except HumError as e:
        return jsonify(ok=False, error=str(e)), 400
    except Exception as e:
        return jsonify(ok=False, error=f"engine error: {e}"), 400
    return jsonify(ok=True, notes=res.notes, key=key, faithful=faithful,
                   midi=f"hum/{uid}.mid", wav=f"hum/{uid}_preview.wav")


@app.get("/file/<kind>/<name>")
def serve(kind, name):
    if kind != "hum":
        return "not found", 404
    return send_from_directory(HUM, name)


_INSTRUMENTS = ",".join(INSTRUMENTS.keys())

INDEX = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hum Studio</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{--bg:#0a0f17;--card:#13202e;--line:#21364a;--ink:#eaf1f8;--muted:#8aa0b4;--mint:#46d6a6;--amber:#f2b24b;--blue:#5ba9f4;--violet:#7c5cff;--red:#ff6b6b}
*{box-sizing:border-box}body{margin:0;color:var(--ink);font-family:Inter,system-ui,sans-serif;
 background:radial-gradient(900px 500px at 85% -10%,rgba(124,92,255,.14),transparent 60%),var(--bg)}
.wrap{max-width:560px;margin:0 auto;padding:26px 18px 60px}
.top{display:flex;align-items:center;gap:11px;margin-bottom:6px}
.logo{width:34px;height:34px;border-radius:9px;background:linear-gradient(140deg,var(--blue),var(--violet));display:grid;place-items:center;font-size:18px}
h1{font-size:21px;margin:0}.sub{color:var(--muted);font-size:14px;margin:2px 0 22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px;margin-bottom:16px}
.rec{display:flex;flex-direction:column;align-items:center;gap:12px}
.recbtn{width:84px;height:84px;border-radius:50%;border:0;cursor:pointer;font-size:30px;
 background:linear-gradient(140deg,var(--blue),var(--violet));color:#06101c;box-shadow:0 0 0 6px rgba(124,92,255,.12)}
.recbtn.on{background:var(--red);animation:pulse 1.2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(255,107,107,.5)}100%{box-shadow:0 0 0 18px rgba(255,107,107,0)}}
.rec .hint{color:var(--muted);font-size:13px}
.or{color:var(--muted);font-size:12px;text-align:center;margin:6px 0}
.up{display:block;text-align:center;color:var(--blue);font-size:13px;cursor:pointer}
audio{width:100%;margin-top:10px}
.grid{display:flex;gap:12px;flex-wrap:wrap}.grid>div{flex:1;min-width:120px}
label{display:block;font-size:12px;color:var(--muted);margin:0 0 6px}
select,input[type=number]{width:100%;padding:10px 11px;background:#0d1722;border:1px solid var(--line);border-radius:10px;color:var(--ink);font-size:14px;font-family:inherit}
.switch{display:flex;align-items:center;gap:10px;margin-top:14px}
.switch input{width:42px;height:24px;appearance:none;background:#0d1722;border:1px solid var(--line);border-radius:99px;position:relative;cursor:pointer;transition:.2s}
.switch input:checked{background:var(--mint)}
.switch input::after{content:"";position:absolute;top:2px;left:2px;width:18px;height:18px;border-radius:50%;background:#fff;transition:.2s}
.switch input:checked::after{left:21px}
.switch .t{font-size:13px}.switch .t b{display:block}.switch .t span{color:var(--muted);font-size:11.5px}
.go{margin-top:18px;width:100%;padding:13px;border:0;border-radius:11px;background:var(--blue);color:#06101c;font-weight:800;font-size:15px;cursor:pointer}
.go:disabled{opacity:.5;cursor:default}
.tag{display:inline-block;font-size:11px;font-weight:700;padding:3px 10px;border-radius:99px;background:rgba(70,214,166,.15);color:var(--mint)}
.dl{display:inline-block;margin-top:12px;background:linear-gradient(140deg,var(--blue),var(--violet));color:#06101c;font-weight:700;padding:11px 16px;border-radius:10px;text-decoration:none}
.err{color:var(--amber);font-size:14px}.note{color:var(--muted);font-size:12px;margin-top:10px}
.spin{display:inline-block;width:15px;height:15px;border:2px solid rgba(255,255,255,.3);border-top-color:#06101c;border-radius:50%;animation:s .7s linear infinite;vertical-align:-2px;margin-right:7px}@keyframes s{to{transform:rotate(360deg)}}
</style></head><body><div class="wrap">
<div class="top"><div class="logo">🎤</div><div><h1>Hum Studio</h1></div></div>
<p class="sub">Hum a bassline or melody → get a clean, in-key instrument part.</p>

<div class="card">
  <div class="rec">
    <button class="recbtn" id="rec" onclick="toggleRec()">●</button>
    <div class="hint" id="rechint">Tap to record your hum</div>
  </div>
  <div class="or">— or —</div>
  <label class="up" for="file">⬆ upload an audio clip instead</label>
  <input type="file" id="file" accept="audio/*" style="display:none" onchange="useFile()">
  <audio id="yourhum" controls style="display:none"></audio>
</div>

<div class="card">
  <div class="grid">
    <div><label>Tempo (BPM)</label><input type="number" id="bpm" value="90" min="40" max="220"></div>
    <div><label>Key</label><select id="key"></select></div>
  </div>
  <div class="grid" style="margin-top:12px">
    <div><label>Instrument</label><select id="instrument"></select></div>
    <div><label>Quantize</label><select id="grid"><option value="8">1/8</option><option value="16" selected>1/16</option><option value="32">1/32</option></select></div>
  </div>
  <div class="switch">
    <input type="checkbox" id="correct" checked>
    <div class="t"><b>Auto-correct to key</b><span>On: snapped in-key · Off: faithful to your hum</span></div>
  </div>
  <button class="go" id="gen" onclick="generate()" disabled>Generate part</button>
</div>

<div id="result"></div>

<script>
const INSTR="__INSTRUMENTS__".split(",");
let rec=null, chunks=[], blob=null;

function fillSelects(){
  const k=document.getElementById("key");const roots=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"];
  roots.forEach(r=>{["maj","min"].forEach(s=>{const o=document.createElement("option");o.value=r+s;o.textContent=r+" "+(s==="maj"?"major":"minor");if(r==="A"&&s==="min")o.selected=true;k.appendChild(o)});});
  const ins=document.getElementById("instrument");INSTR.forEach(n=>{const o=document.createElement("option");o.value=n;o.textContent=n;if(n==="bass")o.selected=true;ins.appendChild(o)});
}
function setRecUI(on){const b=document.getElementById("rec");b.classList.toggle("on",on);b.textContent=on?"■":"●";
  document.getElementById("rechint").textContent=on?"Recording… tap to stop":"Tap to record your hum"}
async function toggleRec(){
  if(rec && rec.state==="recording"){rec.stop();return}
  try{const stream=await navigator.mediaDevices.getUserMedia({audio:true});
    rec=new MediaRecorder(stream);chunks=[];
    rec.ondataavailable=e=>chunks.push(e.data);
    rec.onstop=()=>{blob=new Blob(chunks,{type:rec.mimeType||"audio/webm"});showHum();stream.getTracks().forEach(t=>t.stop());setRecUI(false)};
    rec.start();setRecUI(true);
  }catch(e){alert("Microphone blocked. Allow mic access, or use 'upload a clip'.\n\n"+e)}
}
function useFile(){const f=document.getElementById("file").files[0];if(f){blob=f;showHum()}}
function showHum(){const a=document.getElementById("yourhum");a.src=URL.createObjectURL(blob);a.style.display="block";document.getElementById("gen").disabled=false}

async function generate(){
  if(!blob)return;const btn=document.getElementById("gen");const res=document.getElementById("result");
  const fd=new FormData();
  fd.append("audio",blob,"hum.webm");
  fd.append("bpm",val("bpm"));fd.append("key",val("key"));fd.append("grid",val("grid"));
  fd.append("instrument",val("instrument"));fd.append("faithful",document.getElementById("correct").checked?"0":"1");
  btn.disabled=true;btn.innerHTML='<span class="spin"></span>Generating…';res.innerHTML="";
  try{
    const r=await fetch("/api/hum",{method:"POST",body:fd});const d=await r.json();
    if(!d.ok){res.innerHTML=`<div class="card"><div class="err">⚠ ${d.error}</div></div>`}
    else{res.innerHTML=`<div class="card">
      <span class="tag">✓ ${d.notes} notes · ${d.faithful?"faithful":"key "+d.key}</span>
      <label style="margin-top:12px">Hear your part</label>
      <audio controls autoplay src="/file/${d.wav}"></audio>
      <div><a class="dl" href="/file/${d.midi}" download>⬇ Save MIDI (.mid)</a></div>
      <div class="note">Drag the saved .mid onto any instrument track in your DAW.</div>
    </div>`}
  }catch(e){res.innerHTML=`<div class="card"><div class="err">⚠ ${e}</div></div>`}
  btn.disabled=false;btn.textContent="Generate part";
}
function val(id){return document.getElementById(id).value}
fillSelects();
</script>
</div></body></html>""".replace("__INSTRUMENTS__", _INSTRUMENTS)


if __name__ == "__main__":
    app.run(debug=True, port=5005)
