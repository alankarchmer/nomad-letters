"""Serve the built site (site/index.html) on $PORT, for Railway and similar hosts.

    python main.py            # http://localhost:8000
"""
import functools
import http.server
import os
from pathlib import Path

SITE = Path(__file__).resolve().parent / "site"
PORT = int(os.environ.get("PORT", "8000"))


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "public, max-age=300")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()


if __name__ == "__main__":
    handler = functools.partial(Handler, directory=str(SITE))
    with http.server.ThreadingHTTPServer(("0.0.0.0", PORT), handler) as server:
        print(f"Serving {SITE} on port {PORT}", flush=True)
        server.serve_forever()
