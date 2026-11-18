"""Vercel entry point: receives Yandex Dialogs webhook POST requests and calls skill.handler."""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# The skill logic lives in skill.py in the project root.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from skill import handler as skill_handler  # noqa: E402

FALLBACK = {
    "response": {"text": "Что-то пошло не так. Попробуйте ещё раз позже.", "end_session": True},
    "version": "1.0",
}


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Handy for checking in a browser that the function is deployed.
        self._send(200, {"status": "ok"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            event = json.loads(self.rfile.read(length) or b"{}")
            self._send(200, skill_handler(event))
        except Exception:
            self._send(200, FALLBACK)
