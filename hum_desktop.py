#!/usr/bin/env python3
"""Hum Studio — desktop app.

Runs the Hum Studio in a native window (pywebview). Record a hum, get an
instrument part you can hear and save — no browser needed.

  pip install -r hum2inst/requirements.txt flask pywebview
  brew install ffmpeg
  python hum_desktop.py

Note: recording needs microphone permission. If the native window can't access
the mic on your system, run `python hum_app.py` and use it in your browser.
"""
from __future__ import annotations
import socket
import threading

import webview

from hum_app import app


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main() -> None:
    port = _free_port()
    threading.Thread(target=lambda: app.run(host="127.0.0.1", port=port,
                                            debug=False, use_reloader=False),
                     daemon=True).start()
    webview.create_window("Hum Studio", f"http://127.0.0.1:{port}",
                          width=600, height=860, min_size=(460, 640))
    webview.start()


if __name__ == "__main__":
    main()
