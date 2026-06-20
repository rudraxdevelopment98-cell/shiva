#!/usr/bin/env python3
"""Auto Mix & Master — web product.

Single-page app (Master / Mix / Match) on a JSON API over the engine, with a
freemium usage gate on the client. Same Flask `app` is reused by desktop.py.

  pip install -r requirements.txt      # flask, pywebview, pedalboard, matchering
  brew install ffmpeg
  python app.py                        # → http://127.0.0.1:5000

Making it *sell* (accounts + real payments + server-side limits): see
docs/monetization.md. The client gate here is a demo; real enforcement is server-side.
"""
from __future__ import annotations
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory, Response

from engine import master, analyze, automix, match, chain, reference, EngineError

ROOT = os.path.dirname(os.path.abspath(__file__))
UP = os.path.join(ROOT, "out", "uploads")
OUT = os.path.join(ROOT, "out", "masters")
os.makedirs(UP, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB uploads


def _metrics(a):
    return {"lufs": round(a.integrated_lufs, 1),
            "tp": round(a.true_peak_db, 1),
            "lra": round(a.loudness_range, 1)}


def _save(file, tag):
    ext = os.path.splitext(file.filename)[1] or ".wav"
    name = f"{uuid.uuid4().hex[:8]}_{tag}{ext}"
    path = os.path.join(UP, name)
    file.save(path)
    return name, path


@app.get("/")
def index():
    return Response(INDEX, mimetype="text/html")


@app.get("/api/caps")
def caps():
    return jsonify(chain=chain.available(), reference=reference.available())


@app.post("/api/master")
def api_master():
    f = request.files.get("audio")
    if not f or not f.filename:
        return jsonify(ok=False, error="No file uploaded."), 400
    src_name, src = _save(f, "in")
    out_name = src_name.rsplit(".", 1)[0] + "_master.wav"
    out = os.path.join(OUT, out_name)
    try:
        lufs = float(request.form.get("lufs", -14))
        preset = request.form.get("preset") or None
        before = analyze(src)
        res = master(src, out, target_lufs=lufs, preset=preset)
        after = analyze(out)
    except EngineError as e:
        return jsonify(ok=False, error=str(e)), 400
    return jsonify(ok=True, kind="master", preset=res.preset,
                   src=f"uploads/{src_name}", file=f"masters/{out_name}",
                   before=_metrics(before), after=_metrics(after))


@app.post("/api/mix")
def api_mix():
    files = [f for f in request.files.getlist("stems") if f and f.filename]
    if len(files) < 2:
        return jsonify(ok=False, error="Select at least two stems."), 400
    paths = [_save(f, f"stem{i}")[1] for i, f in enumerate(files)]
    out_name = uuid.uuid4().hex[:8] + "_mix.wav"
    out = os.path.join(OUT, out_name)
    try:
        lufs = float(request.form.get("lufs", -14))
        preset = request.form.get("preset") or None
        res = automix(paths, out, target_lufs=lufs, preset=preset)
        after = analyze(out)
    except EngineError as e:
        return jsonify(ok=False, error=str(e)), 400
    return jsonify(ok=True, kind="mix", stems=res.stems, preset=res.preset,
                   file=f"masters/{out_name}", after=_metrics(after))


@app.post("/api/match")
def api_match():
    tgt = request.files.get("target")
    ref = request.files.get("reference")
    if not tgt or not tgt.filename or not ref or not ref.filename:
        return jsonify(ok=False, error="Pick both your track and a reference."), 400
    _, tp = _save(tgt, "target")
    _, rp = _save(ref, "ref")
    out_name = uuid.uuid4().hex[:8] + "_matched.wav"
    out = os.path.join(OUT, out_name)
    try:
        match(tp, rp, out)
        after = analyze(out)
    except EngineError as e:
        return jsonify(ok=False, error=str(e)), 400
    return jsonify(ok=True, kind="match", file=f"masters/{out_name}", after=_metrics(after))


@app.get("/file/<kind>/<name>")
def serve(kind, name):
    folder = {"uploads": UP, "masters": OUT}.get(kind)
    if not folder:
        return "not found", 404
    return send_from_directory(folder, name)


INDEX = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mastr — Auto Mix & Master</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{--bg:#0b121a;--bg2:#0e1622;--card:#13202e;--line:#21364a;--ink:#e7eef6;--muted:#8aa0b4;
--mint:#46d6a6;--amber:#f2b24b;--red:#ff6b6b;--blue:#5ba9f4}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,system-ui,sans-serif}
body{background:radial-gradient(900px 500px at 85% -10%,rgba(91,169,244,.10),transparent 60%),
 radial-gradient(700px 500px at 0% 110%,rgba(70,214,166,.08),transparent 60%),var(--bg)}
.top{display:flex;align-items:center;gap:12px;padding:16px 22px;border-bottom:1px solid var(--line);position:sticky;top:0;background:rgba(11,18,26,.85);backdrop-filter:blur(8px);z-index:10}
.logo{width:34px;height:34px;border-radius:9px;background:linear-gradient(140deg,var(--blue),#7c5cff);display:grid;place-items:center;font-size:18px}
.brand b{font-size:15px}.brand small{display:block;color:var(--muted);font-size:10px;letter-spacing:2px}
.meter{margin-left:auto;font-size:12px;color:var(--muted);display:flex;align-items:center;gap:10px}
.meter .pro{background:rgba(70,214,166,.15);color:var(--mint);font-weight:700;padding:3px 10px;border-radius:99px}
.meter button{background:linear-gradient(140deg,var(--blue),#7c5cff);border:0;color:#04101c;font-weight:700;padding:7px 13px;border-radius:9px;cursor:pointer}
.wrap{max-width:640px;margin:0 auto;padding:26px 16px 60px}
h1{font-size:24px;margin:6px 0 2px}.sub{color:var(--muted);margin:0 0 22px;font-size:14px}
.tabs{display:flex;gap:6px;background:var(--bg2);border:1px solid var(--line);border-radius:12px;padding:5px;margin-bottom:18px}
.tabs button{flex:1;background:transparent;border:0;color:var(--muted);font-weight:600;font-size:14px;padding:10px;border-radius:9px;cursor:pointer;font-family:inherit}
.tabs button.on{background:var(--card);color:var(--ink);box-shadow:0 1px 0 rgba(255,255,255,.04)}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin-bottom:16px}
.drop{border:1.5px dashed var(--line);border-radius:12px;padding:26px;text-align:center;color:var(--muted);cursor:pointer;transition:.15s}
.drop:hover,.drop.hot{border-color:var(--blue);background:rgba(91,169,244,.06);color:var(--ink)}
.drop b{color:var(--ink)}.files{font-size:12px;color:var(--mint);margin-top:8px;font-family:"JetBrains Mono",monospace}
.two{display:flex;gap:12px}.two>div{flex:1}
label{display:block;font-size:12px;color:var(--muted);margin:14px 0 6px}
select{width:100%;padding:11px 12px;background:#0d1722;border:1px solid var(--line);border-radius:10px;color:var(--ink);font-size:14px;font-family:inherit}
.go{margin-top:18px;width:100%;padding:13px;border:0;border-radius:11px;background:var(--blue);color:#04101c;font-weight:700;font-size:15px;cursor:pointer}
.go:disabled{opacity:.5;cursor:default}
.mono{font-family:"JetBrains Mono",monospace}
.metrics{display:flex;gap:12px;flex-wrap:wrap;margin-top:14px}
.m{flex:1;min-width:120px;background:#0d1722;border:1px solid var(--line);border-radius:10px;padding:12px}
.m .k{font-size:11px;color:var(--muted)}.m .v{font-size:20px;font-weight:700;margin-top:3px}
.m .was{font-size:11px;color:var(--muted);margin-top:3px}
.tag{display:inline-block;font-size:11px;font-weight:700;padding:3px 10px;border-radius:99px;background:rgba(70,214,166,.15);color:var(--mint)}
audio{width:100%;margin-top:10px}.dl{display:inline-block;margin-top:12px;color:var(--blue);font-weight:600;text-decoration:none}
.err{color:var(--amber);font-size:14px}.note{font-size:12px;color:var(--muted);margin-top:8px}
.spin{display:inline-block;width:16px;height:16px;border:2px solid rgba(255,255,255,.3);border-top-color:#04101c;border-radius:50%;animation:s .7s linear infinite;vertical-align:-3px;margin-right:8px}
@keyframes s{to{transform:rotate(360deg)}}
.modal-bg{position:fixed;inset:0;background:rgba(4,9,15,.7);display:none;place-items:center;z-index:50;padding:20px}
.modal-bg.show{display:grid}
.modal{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:26px;max-width:380px;width:100%;text-align:center}
.modal h3{margin:0 0 6px;font-size:20px}.modal p{color:var(--muted);font-size:14px;margin:0 0 18px}
.price{font-size:30px;font-weight:700;margin:6px 0}.price span{font-size:14px;color:var(--muted);font-weight:500}
.modal .go{margin-top:4px}.modal .x{margin-top:12px;background:none;border:0;color:var(--muted);cursor:pointer;font-size:13px}
.plist{text-align:left;font-size:13px;color:var(--ink);margin:14px 0;padding:0;list-style:none}
.plist li{padding:5px 0}.plist li::before{content:"✓ ";color:var(--mint);font-weight:700}
.code{width:100%;padding:10px;background:#0d1722;border:1px solid var(--line);border-radius:9px;color:var(--ink);margin-top:10px;font-family:inherit}
</style></head><body>
<div class="top">
  <div class="logo">🎚️</div><div class="brand"><b>Mastr</b><small>AUTO MIX &amp; MASTER</small></div>
  <div class="meter" id="meter"></div>
</div>
<div class="wrap">
  <h1>Make it sound finished.</h1>
  <p class="sub">Upload your music and get a polished, loudness-correct master in seconds.</p>
  <div class="tabs">
    <button class="on" data-tab="master" onclick="setTab('master')">Master</button>
    <button data-tab="mix" onclick="setTab('mix')">Auto-mix</button>
    <button data-tab="match" onclick="setTab('match')">Reference</button>
  </div>

  <div class="card" id="panel"></div>
  <div id="result"></div>
</div>

<div class="modal-bg" id="paywall"><div class="modal">
  <h3>Go Pro 🚀</h3>
  <p>You've used your free renders. Upgrade for unlimited mixing &amp; mastering.</p>
  <div class="price">£6<span>/month</span></div>
  <ul class="plist"><li>Unlimited masters &amp; mixes</li><li>Reference matching</li><li>High-quality WAV export</li><li>No watermark</li></ul>
  <button class="go" onclick="goPro()">Upgrade to Pro</button>
  <input class="code" id="code" placeholder="Have an access code?">
  <button class="x" onclick="redeem()">Redeem code</button>
  <div><button class="x" onclick="hidePaywall()">Maybe later</button></div>
</div></div>

<script>
const FREE_LIMIT=3;
let caps={chain:false,reference:false}, tab="master", picked={};

function uses(){return +(localStorage.getItem("amm_uses")||0)}
function isPro(){return localStorage.getItem("amm_pro")==="1"}
function bump(){localStorage.setItem("amm_uses",uses()+1);drawMeter()}
function drawMeter(){const m=document.getElementById("meter");
  m.innerHTML=isPro()?`<span class="pro">PRO · unlimited</span>`
    :`<span>Free: ${Math.min(uses(),FREE_LIMIT)}/${FREE_LIMIT} used</span><button onclick="showPaywall()">Go Pro</button>`}
function showPaywall(){document.getElementById("paywall").classList.add("show")}
function hidePaywall(){document.getElementById("paywall").classList.remove("show")}
function goPro(){ // placeholder — real checkout (Stripe) plugs in here; see docs/monetization.md
  alert("Checkout goes here (Stripe). For now, use an access code to unlock.");}
function redeem(){if(document.getElementById("code").value.trim().toUpperCase()==="LAUNCH"){
  localStorage.setItem("amm_pro","1");hidePaywall();drawMeter();alert("Pro unlocked 🎉");}else alert("Invalid code.")}
function gateOk(){if(isPro())return true;if(uses()>=FREE_LIMIT){showPaywall();return false}return true}

const PANELS={
 master:()=>`<div class="drop" id="dz" onclick="pick('audio')">
    <div style="font-size:26px">🎵</div><b>Drop your mix</b> or click to choose<div class="files" id="f-audio"></div></div>
   <input type="file" id="audio" accept="audio/*" style="display:none" onchange="onPick('audio')">
   <div class="two">${lufsSel()}${presetSel()}</div>
   <button class="go" id="run" onclick="run()">Master it</button>`,
 mix:()=>`<div class="drop" onclick="pick('stems')">
    <div style="font-size:26px">🎚️</div><b>Drop 2+ stems</b> (drums, bass, vocals…)<div class="files" id="f-stems"></div></div>
   <input type="file" id="stems" accept="audio/*" multiple style="display:none" onchange="onPick('stems')">
   <div class="two">${lufsSel()}${presetSel()}</div>
   <button class="go" id="run" onclick="run()">Mix &amp; master</button>`,
 match:()=>`<div class="two">
     <div class="drop" onclick="pick('target')"><b>Your track</b><div class="files" id="f-target"></div></div>
     <div class="drop" onclick="pick('reference')"><b>Reference song</b><div class="files" id="f-reference"></div></div></div>
   <input type="file" id="target" accept="audio/*" style="display:none" onchange="onPick('target')">
   <input type="file" id="reference" accept="audio/*" style="display:none" onchange="onPick('reference')">
   ${caps.reference?"":`<div class="note">⚠ Reference matching needs <span class="mono">matchering</span> installed.</div>`}
   <button class="go" id="run" onclick="run()">Match to reference</button>`,
};
function lufsSel(){return `<div><label>Loudness target</label><select id="lufs">
  <option value="-14">-14 LUFS · Streaming</option><option value="-9">-9 LUFS · Loud / club</option>
  <option value="-16">-16 LUFS · Podcast</option></select></div>`}
function presetSel(){return `<div><label>Tone preset${caps.chain?"":" (needs pedalboard)"}</label><select id="preset">
  <option value="">None (loudness only)</option><option value="clean">Clean</option>
  <option value="warm">Warm</option><option value="bright">Bright</option><option value="loud">Loud</option></select></div>`}

function setTab(t){tab=t;picked={};document.querySelectorAll(".tabs button").forEach(b=>b.classList.toggle("on",b.dataset.tab===t));
  document.getElementById("panel").innerHTML=PANELS[t]();document.getElementById("result").innerHTML=""}
function pick(id){document.getElementById(id).click()}
function onPick(id){const el=document.getElementById(id);picked[id]=el.files;
  const names=[...el.files].map(f=>f.name).join(", ");const box=document.getElementById("f-"+id);if(box)box.textContent=names}

async function run(){
  if(!gateOk())return;
  const btn=document.getElementById("run");const res=document.getElementById("result");
  const fd=new FormData();let url;
  if(tab==="master"){if(!picked.audio)return toast("Choose a file first.");
    fd.append("audio",picked.audio[0]);fd.append("lufs",v("lufs"));fd.append("preset",v("preset"));url="/api/master"}
  else if(tab==="mix"){if(!picked.stems||picked.stems.length<2)return toast("Pick at least two stems.");
    [...picked.stems].forEach(f=>fd.append("stems",f));fd.append("lufs",v("lufs"));fd.append("preset",v("preset"));url="/api/mix"}
  else{if(!picked.target||!picked.reference)return toast("Pick both files.");
    fd.append("target",picked.target[0]);fd.append("reference",picked.reference[0]);url="/api/match"}
  btn.disabled=true;btn.innerHTML=`<span class="spin"></span>Processing…`;res.innerHTML="";
  try{
    const r=await fetch(url,{method:"POST",body:fd});const d=await r.json();
    if(!d.ok){res.innerHTML=card(`<div class="err">⚠ ${d.error}</div>`);}
    else{bump();res.innerHTML=renderResult(d);}
  }catch(e){res.innerHTML=card(`<div class="err">⚠ ${e}</div>`);}
  btn.disabled=false;btn.textContent=tab==="master"?"Master it":tab==="mix"?"Mix & master":"Match to reference";
}
function v(id){const e=document.getElementById(id);return e?e.value:""}
function toast(m){document.getElementById("result").innerHTML=card(`<div class="err">${m}</div>`)}
function card(inner){return `<div class="card">${inner}</div>`}
function metric(k,val,unit,was){return `<div class="m"><div class="k">${k}</div><div class="v mono">${val} <span style="font-size:12px;color:var(--muted)">${unit}</span></div>${was!=null?`<div class="was mono">was ${was}</div>`:""}</div>`}
function renderResult(d){
  const a=d.after,b=d.before||{};const head=d.kind==="match"?"✓ matched to reference":d.kind==="mix"?`✓ mixed ${d.stems} stems`:"✓ mastered";
  const metrics=`<div class="metrics">
    ${metric("Loudness",a.lufs,"LUFS",b.lufs)}${metric("True peak",a.tp,"dBTP",b.tp)}${metric("Dynamic range",a.lra,"LU",b.lra)}</div>`;
  const before=d.src?`<label>Before</label><audio controls src="/file/${d.src}"></audio>`:"";
  return card(`<span class="tag">${head}${d.preset?" · "+d.preset:""}</span>${metrics}
    ${before}<label style="margin-top:10px">After</label><audio controls src="/file/${d.file}"></audio>
    <a class="dl" href="/file/${d.file}" download>⬇ Download</a>`);
}

(async function init(){
  try{caps=await (await fetch("/api/caps")).json()}catch(e){}
  drawMeter();setTab("master");
  // drag & drop on the master dropzone
  document.addEventListener("dragover",e=>e.preventDefault());
})();
</script>
</body></html>"""


if __name__ == "__main__":
    app.run(debug=True, port=5000)
