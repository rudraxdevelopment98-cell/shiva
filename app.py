#!/usr/bin/env python3
"""Auto Mix & Master — local web app.

A tiny Flask UI on top of the engine: upload a track, pick a loudness target +
preset, get a master back with before/after metrics and an A/B player.

  pip install flask          # plus: brew install ffmpeg  (and optional: pedalboard)
  python app.py              # → http://127.0.0.1:5000
"""
from __future__ import annotations
import os
import uuid
from flask import Flask, request, send_from_directory, render_template_string

from engine import master, analyze, automix, chain, EngineError

ROOT = os.path.dirname(os.path.abspath(__file__))
UP = os.path.join(ROOT, "out", "uploads")
OUT = os.path.join(ROOT, "out", "masters")
os.makedirs(UP, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

app = Flask(__name__)

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Auto Mix & Master</title>
<style>
:root{--bg:#0b121a;--card:#13202e;--line:#21364a;--ink:#e7eef6;--muted:#8aa0b4;
--mint:#46d6a6;--amber:#f2b24b;--blue:#5ba9f4}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font-family:Inter,system-ui,sans-serif;padding:32px 16px;display:flex;justify-content:center}
.wrap{width:100%;max-width:680px}h1{font-size:22px;margin:0 0 4px}
.sub{color:var(--muted);margin:0 0 24px;font-size:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;margin-bottom:18px}
label{display:block;font-size:13px;color:var(--muted);margin:0 0 6px}
input,select{width:100%;padding:11px 12px;background:#0d1722;border:1px solid var(--line);
border-radius:10px;color:var(--ink);font-size:14px;font-family:inherit}
.row{display:flex;gap:12px}.row>div{flex:1}
button{margin-top:16px;width:100%;padding:12px;border:0;border-radius:10px;background:var(--blue);
color:#04101c;font-weight:700;font-size:15px;cursor:pointer}
.mono{font-family:"JetBrains Mono",ui-monospace,monospace}
.metrics{display:flex;gap:14px;flex-wrap:wrap}
.m{flex:1;min-width:150px;background:#0d1722;border:1px solid var(--line);border-radius:10px;padding:12px}
.m .k{font-size:11px;color:var(--muted)}.m .v{font-size:20px;font-weight:700;margin-top:3px}
.tag{display:inline-block;font-size:11px;font-weight:700;padding:3px 9px;border-radius:99px}
.tag.ok{background:rgba(70,214,166,.15);color:var(--mint)}
audio{width:100%;margin-top:8px}.err{color:var(--amber);font-size:14px}
.dl{display:inline-block;margin-top:14px;color:var(--blue);font-weight:600;text-decoration:none}
</style></head><body><div class="wrap">
<h1>🎚️ Auto Mix &amp; Master</h1>
<p class="sub">Drop in a mix → get a loudness-correct master. {{ chain_note }}</p>
<form class="card" method="post" enctype="multipart/form-data" action="/master">
  <label>Audio file (wav / mp3 / flac)</label>
  <input type="file" name="audio" accept="audio/*" required>
  <div class="row" style="margin-top:14px">
    <div><label>Loudness target (LUFS)</label>
      <select name="lufs"><option value="-14">-14 · Streaming</option>
        <option value="-9">-9 · Loud / club</option><option value="-16">-16 · Podcast</option></select></div>
    <div><label>Tone preset</label>
      <select name="preset"><option value="">None (loudness only)</option>
        <option value="clean">Clean</option><option value="warm">Warm</option>
        <option value="bright">Bright</option><option value="loud">Loud</option></select></div>
  </div>
  <button type="submit">Master it</button>
</form>

<form class="card" method="post" enctype="multipart/form-data" action="/mix">
  <label>Auto-mix stems — pick 2+ files (drums, bass, vocals…)</label>
  <input type="file" name="stems" accept="audio/*" multiple required>
  <div class="row" style="margin-top:14px">
    <div><label>Final loudness (LUFS)</label>
      <select name="lufs"><option value="-14">-14 · Streaming</option>
        <option value="-9">-9 · Loud / club</option><option value="-16">-16 · Podcast</option></select></div>
    <div><label>Bus tone preset</label>
      <select name="preset"><option value="">None (loudness only)</option>
        <option value="clean">Clean</option><option value="warm">Warm</option>
        <option value="bright">Bright</option><option value="loud">Loud</option></select></div>
  </div>
  <button type="submit">Mix &amp; master stems</button>
</form>
{% if mix_result %}
<div class="card">
  <span class="tag ok">✓ mixed {{ mix_result.stems }} stems{% if mix_result.preset %} · {{ mix_result.preset }}{% endif %}</span>
  <div class="metrics" style="margin-top:14px">
    <div class="m"><div class="k">Loudness</div><div class="v mono">{{ '%.1f'|format(mix_after.integrated_lufs) }} <span style="font-size:12px;color:var(--muted)">LUFS</span></div></div>
    <div class="m"><div class="k">True peak</div><div class="v mono">{{ '%.1f'|format(mix_after.true_peak_db) }} <span style="font-size:12px;color:var(--muted)">dBTP</span></div></div>
    <div class="m"><div class="k">Dynamic range</div><div class="v mono">{{ '%.1f'|format(mix_after.loudness_range) }} <span style="font-size:12px;color:var(--muted)">LU</span></div></div>
  </div>
  <label style="margin-top:14px">Mixed master</label><audio controls src="/file/masters/{{ mix_result.out_name }}"></audio>
  <a class="dl" href="/file/masters/{{ mix_result.out_name }}" download>⬇ Download mix</a>
</div>
{% endif %}
{% if result %}
<div class="card">
  <span class="tag ok">✓ mastered{% if result.preset %} · {{ result.preset }}{% endif %}</span>
  <div class="metrics" style="margin-top:14px">
    <div class="m"><div class="k">Loudness</div><div class="v mono">{{ '%.1f'|format(after.integrated_lufs) }} <span style="font-size:12px;color:var(--muted)">LUFS</span></div>
      <div class="k mono" style="margin-top:4px">was {{ '%.1f'|format(before.integrated_lufs) }}</div></div>
    <div class="m"><div class="k">True peak</div><div class="v mono">{{ '%.1f'|format(after.true_peak_db) }} <span style="font-size:12px;color:var(--muted)">dBTP</span></div>
      <div class="k mono" style="margin-top:4px">was {{ '%.1f'|format(before.true_peak_db) }}</div></div>
    <div class="m"><div class="k">Dynamic range</div><div class="v mono">{{ '%.1f'|format(after.loudness_range) }} <span style="font-size:12px;color:var(--muted)">LU</span></div>
      <div class="k mono" style="margin-top:4px">was {{ '%.1f'|format(before.loudness_range) }}</div></div>
  </div>
  <label style="margin-top:16px">Before</label><audio controls src="/file/uploads/{{ result.src_name }}"></audio>
  <label style="margin-top:10px">After</label><audio controls src="/file/masters/{{ result.out_name }}"></audio>
  <a class="dl" href="/file/masters/{{ result.out_name }}" download>⬇ Download master</a>
</div>
{% endif %}
{% if error %}<div class="card"><div class="err">⚠ {{ error }}</div></div>{% endif %}
</div></body></html>"""


@app.get("/")
def index():
    note = "Tone presets active." if chain.available() else "Install pedalboard for tone presets."
    return render_template_string(PAGE, chain_note=note, result=None, error=None)


@app.post("/master")
def do_master():
    note = "Tone presets active." if chain.available() else "Install pedalboard for tone presets."
    f = request.files.get("audio")
    if not f or not f.filename:
        return render_template_string(PAGE, chain_note=note, error="No file uploaded.", result=None)
    uid = uuid.uuid4().hex[:8]
    ext = os.path.splitext(f.filename)[1] or ".wav"
    src_name = f"{uid}{ext}"
    src = os.path.join(UP, src_name)
    f.save(src)
    out_name = f"{uid}_master.wav"
    out = os.path.join(OUT, out_name)
    try:
        lufs = float(request.form.get("lufs", -14))
        preset = request.form.get("preset") or None
        before = analyze(src)
        res = master(src, out, target_lufs=lufs, preset=preset)
        after = analyze(out)
    except EngineError as e:
        return render_template_string(PAGE, chain_note=note, error=str(e), result=None)
    return render_template_string(PAGE, chain_note=note, before=before, after=after,
        result={"src_name": src_name, "out_name": out_name, "preset": res.preset}, error=None)


@app.post("/mix")
def do_mix():
    note = "Tone presets active." if chain.available() else "Install pedalboard for tone presets."
    files = [f for f in request.files.getlist("stems") if f and f.filename]
    if len(files) < 2:
        return render_template_string(PAGE, chain_note=note, error="Select at least two stems.", result=None)
    uid = uuid.uuid4().hex[:8]
    paths = []
    for i, f in enumerate(files):
        ext = os.path.splitext(f.filename)[1] or ".wav"
        sp = os.path.join(UP, f"{uid}_stem{i}{ext}")
        f.save(sp)
        paths.append(sp)
    out_name = f"{uid}_mix.wav"
    out = os.path.join(OUT, out_name)
    try:
        lufs = float(request.form.get("lufs", -14))
        preset = request.form.get("preset") or None
        res = automix(paths, out, target_lufs=lufs, preset=preset)
        after = analyze(out)
    except EngineError as e:
        return render_template_string(PAGE, chain_note=note, error=str(e), result=None)
    return render_template_string(PAGE, chain_note=note, mix_after=after,
        mix_result={"out_name": out_name, "stems": res.stems, "preset": res.preset}, error=None)


@app.get("/file/<kind>/<name>")
def serve(kind, name):
    folder = {"uploads": UP, "masters": OUT}.get(kind)
    if not folder:
        return "not found", 404
    return send_from_directory(folder, name)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
