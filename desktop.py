#!/usr/bin/env python3
"""Auto Mix & Master — desktop app.

Runs the engine behind a native window (no browser needed). Same UI as app.py,
wrapped with pywebview so it feels like a real Mac/desktop application.

  pip install -r requirements.txt        # flask + pywebview (+ optional pedalboard)
  brew install ffmpeg
  python desktop.py
"""
from __future__ import annotations
import socket
import threading

import webview  # pywebview

from app import app


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _serve(port: int) -> None:
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def main() -> None:
    port = _free_port()
    threading.Thread(target=_serve, args=(port,), daemon=True).start()
    webview.create_window(
        "Auto Mix & Master",
        f"http://127.0.0.1:{port}",
        width=780, height=920, min_size=(560, 640),
    )
    webview.start()


if __name__ == "__main__":
    main()
