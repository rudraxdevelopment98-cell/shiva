"""SonicDNA — API + web analysis MVP (FastAPI).

Upload a track → real DSP features (librosa) → Emotional DNA (valence/arousal
model) + timeline heatmap. v0 emotion is a transparent heuristic; swap in a
trained model behind `emotion.dna_from_va` later.

  pip install -r requirements.txt        # + brew install ffmpeg
  uvicorn main:app --reload              # http://127.0.0.1:8000
"""
from __future__ import annotations
import os
import tempfile
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

import emotion as em
from features import analyze_track, FeatureError

app = FastAPI(title="SonicDNA API", version="0.2.0")
_DB: dict[str, dict] = {}


@app.get("/health")
def health():
    return {"ok": True, "taxonomy": len(em.TAXONOMY), "model": "va-heuristic-0"}


@app.post("/v1/analyze", status_code=201)
async def analyze(file: UploadFile = File(...)):
    data = await file.read()
    if not data:
        raise HTTPException(400, "empty file")
    if len(data) > 80 * 1024 * 1024:
        raise HTTPException(413, "file too large")
    tmp = tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.filename or "")[1] or ".wav", delete=False).name
    with open(tmp, "wb") as f:
        f.write(data)
    try:
        res = analyze_track(tmp)
    except FeatureError as e:
        raise HTTPException(400, str(e))
    finally:
        os.path.exists(tmp) and os.remove(tmp)

    v, a = res["va"]
    dna = em.dna_from_va(v, a)
    timeline = [{"t0": s["t0"], "t1": s["t1"], "dna": em.dna_from_va(*s["va"])}
                for s in res["timeline"]]
    aid = uuid.uuid4().hex[:12]
    out = {"id": aid, "status": "done", "model_version": "va-heuristic-0",
           "filename": file.filename, "features": res["features"],
           "valence": round(v, 3), "arousal": round(a, 3),
           "dna": dna, "top": [{"emotion": e, "score": s} for e, s in em.top(dna, 6)],
           "timeline": timeline}
    _DB[aid] = out
    return out


@app.get("/v1/analyses/{aid}")
def get_analysis(aid: str):
    a = _DB.get(aid)
    if not a:
        raise HTTPException(404, "not found")
    return JSONResponse({k: a[k] for k in ("id", "status", "model_version", "features",
                                           "valence", "arousal", "dna", "top")})


@app.get("/v1/analyses/{aid}/timeline")
def get_timeline(aid: str):
    a = _DB.get(aid)
    if not a:
        raise HTTPException(404, "not found")
    return a["timeline"]


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>SonicDNA</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{--bg:#0a0e17;--card:#141c2b;--line:#243149;--ink:#eaf1f8;--muted:#8aa0b4}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(900px 500px at 85% -10%,rgba(124,92,255,.16),transparent 60%),var(--bg);color:var(--ink);font-family:Inter,system-ui,sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:26px 18px 60px}
.top{display:flex;align-items:center;gap:11px}.logo{width:34px;height:34px;border-radius:9px;background:linear-gradient(140deg,#5ba9f4,#7c5cff);display:grid;place-items:center;font-size:18px}
h1{font-size:21px;margin:0}.sub{color:var(--muted);font-size:14px;margin:2px 0 22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px;margin-bottom:16px}
.up{border:1.5px dashed var(--line);border-radius:12px;padding:24px;text-align:center;color:var(--muted);cursor:pointer}
.up:hover{border-color:#5ba9f4;color:var(--ink)}
.go{margin-top:14px;width:100%;padding:12px;border:0;border-radius:11px;background:#5ba9f4;color:#06101c;font-weight:800;font-size:15px;cursor:pointer}
.go:disabled{opacity:.5}
.bar{display:flex;align-items:center;gap:10px;margin:7px 0}.bar .n{width:110px;font-size:13px;text-transform:capitalize}
.bar .t{flex:1;height:12px;background:#0d1626;border-radius:99px;overflow:hidden}.bar .t i{display:block;height:100%;background:linear-gradient(90deg,#5ba9f4,#7c5cff);border-radius:99px}
.bar .v{width:52px;text-align:right;font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--muted)}
.feat{display:flex;gap:10px;flex-wrap:wrap}.feat div{background:#0d1626;border:1px solid var(--line);border-radius:9px;padding:9px 11px;font-size:12px;color:var(--muted)}
.feat b{color:var(--ink);font-family:"JetBrains Mono",monospace;display:block;font-size:15px}
.hm{display:grid;gap:3px;overflow-x:auto}.hmrow{display:grid;grid-auto-flow:column;gap:3px;align-items:center}
.hlbl{width:96px;font-size:12px;text-transform:capitalize;color:var(--muted);position:sticky;left:0}
.cell{width:26px;height:20px;border-radius:4px}
h3{font-size:13px;color:var(--muted);margin:0 0 12px;letter-spacing:.4px;text-transform:uppercase}
.err{color:#f2b24b}.spin{display:inline-block;width:15px;height:15px;border:2px solid rgba(255,255,255,.3);border-top-color:#06101c;border-radius:50%;animation:s .7s linear infinite;vertical-align:-2px;margin-right:7px}@keyframes s{to{transform:rotate(360deg)}}
</style></head><body><div class="wrap">
<div class="top"><div class="logo">🧬</div><div><h1>SonicDNA</h1></div></div>
<p class="sub">Upload a track → its Emotional DNA + a timeline heatmap. (v0 heuristic model)</p>
<div class="card">
  <div class="up" id="dz" onclick="document.getElementById('f').click()">🎵 <b>Choose an audio file</b> (wav / mp3 / flac)<div id="fn" style="margin-top:6px;font-size:12px"></div></div>
  <input type="file" id="f" accept="audio/*" style="display:none" onchange="document.getElementById('fn').textContent=this.files[0]?.name||''">
  <button class="go" onclick="run()">Analyze</button>
</div>
<div id="out"></div>
<script>
const EMO_HUE={joy:50,euphoria:48,excitement:40,playfulness:55,triumph:45,awe:190,love:330,romance:320,tenderness:300,hope:150,gratitude:140,serenity:170,contentment:120,nostalgia:35,longing:280,melancholy:230,bittersweet:260,wistfulness:250,catharsis:20,sadness:220,grief:225,loneliness:235,despair:240,regret:245,anger:0,tension:10,fear:275,anxiety:290,menace:295,mystery:265,confidence:100,power:15,determination:90,rebellion:5,dreamy:200,meditative:185};
function col(e,p){const h=EMO_HUE[e]??210;return `hsla(${h},70%,55%,${0.12+0.88*p})`}
async function run(){
  const f=document.getElementById('f').files[0]; if(!f)return alert('Choose a file');
  const btn=document.querySelector('.go'); const out=document.getElementById('out');
  btn.disabled=true; btn.innerHTML='<span class=spin></span>Analyzing…'; out.innerHTML='';
  const fd=new FormData(); fd.append('file',f);
  try{
    const r=await fetch('/v1/analyze',{method:'POST',body:fd}); const d=await r.json();
    if(!r.ok){out.innerHTML=`<div class="card err">⚠ ${d.detail||'error'}</div>`}
    else out.innerHTML=render(d);
  }catch(e){out.innerHTML=`<div class="card err">⚠ ${e}</div>`}
  btn.disabled=false; btn.textContent='Analyze';
}
function render(d){
  const bars=d.top.map(t=>`<div class="bar"><div class="n">${t.emotion}</div><div class="t"><i style="width:${(t.score*100).toFixed(0)}%"></i></div><div class="v">${(t.score*100).toFixed(0)}%</div></div>`).join('');
  const f=d.features;
  const feats=[['BPM',f.bpm],['Key',f.key+' '+f.mode],['Loudness (RMS)',f.rms],['Dynamics',f.crest_db+' dB'],['Brightness',f.spectral_centroid_hz+' Hz'],['Duration',f.duration_s+'s'],['Valence',d.valence],['Arousal',d.arousal]]
    .map(x=>`<div>${x[0]}<b>${x[1]}</b></div>`).join('');
  // heatmap: top-6 emotions (rows) × timeline segments (cols)
  const emos=d.top.map(t=>t.emotion);
  const rows=emos.map(e=>{
    const cells=d.timeline.map(s=>`<div class="cell" title="${e} ${(s.dna[e]*100).toFixed(0)}%" style="background:${col(e,s.dna[e])}"></div>`).join('');
    return `<div class="hmrow"><div class="hlbl">${e}</div>${cells}</div>`;
  }).join('');
  return `<div class="card"><h3>Emotional DNA</h3>${bars}</div>
   <div class="card"><h3>Timeline heatmap (start → end)</h3><div class="hm">${rows}</div></div>
   <div class="card"><h3>Features</h3><div class="feat">${feats}</div></div>`;
}
</script>
</div></body></html>"""
