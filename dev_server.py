#!/usr/bin/env python3
"""Serve the static workshop site locally with automatic browser reloads."""

from __future__ import annotations

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
WATCHED_SUFFIXES = {
    ".css",
    ".gif",
    ".html",
    ".jpeg",
    ".jpg",
    ".js",
    ".json",
    ".png",
    ".svg",
    ".webp",
    ".xml",
}


def site_version() -> int:
    """Return the newest modification timestamp among browser-facing files."""
    newest = 0
    for directory, names, files in os.walk(ROOT):
        names[:] = [name for name in names if not name.startswith(".")]
        for filename in files:
            path = Path(directory, filename)
            if path.suffix.lower() in WATCHED_SUFFIXES:
                try:
                    newest = max(newest, path.stat().st_mtime_ns)
                except FileNotFoundError:
                    pass
    return newest


class LiveReloadHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self) -> None:
        if urlparse(self.path).path == "/__dev_version":
            payload = json.dumps({"version": site_version()}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()

def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    handler = lambda *args, **kwargs: LiveReloadHandler(*args, directory=ROOT, **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"GeoIndustry dev server: http://localhost:{port}")
    print("Edit HTML, CSS, or JavaScript and the browser will refresh automatically.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDev server stopped.")


if __name__ == "__main__":
    main()
