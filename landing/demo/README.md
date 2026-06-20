# Demo audio goes here

Add short (15–30s) before/after clips so the landing page can prove the product:

```
demo1-before.mp3   demo1-after.mp3
demo2-before.mp3   demo2-after.mp3
```

Make them by running a real track through the engine:

```bash
python cli.py master your-track.wav demo1-after.wav --lufs -14 --preset warm
# then export ~20s MP3 clips of the original and the master (ffmpeg):
ffmpeg -i your-track.wav  -t 20 -b:a 192k demo1-before.mp3
ffmpeg -i demo1-after.wav -t 20 -b:a 192k demo1-after.mp3
```

Use **your own** audio (or royalty-free), and keep clips short so the page loads fast.
These files are intentionally allowed past `.gitignore` so they ship with the site.
