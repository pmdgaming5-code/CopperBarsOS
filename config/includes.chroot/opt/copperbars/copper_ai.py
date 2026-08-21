#!/usr/bin/env python3
"""CopperBarsOS local AI gateway.

The gateway is intentionally backend-agnostic. It prefers a local Ollama
instance and can be switched to another local OpenAI-compatible endpoint.
No remote endpoint is contacted by default.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os, pathlib, urllib.request

HOST = "127.0.0.1"
PORT = int(os.environ.get("COPPER_PORT", "8765"))
MODEL_DIR = pathlib.Path(os.environ.get("COPPER_MODEL_DIR", "/opt/copperbars/models"))
OLLAMA_URL = os.environ.get("COPPER_OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.environ.get("COPPER_MODEL", "")

SYSTEM_PROMPT = (
    "You are Copper, the friendly local AI assistant built into CopperBarsOS. "
    "Speak Turkish when the user speaks Turkish. Be concise, accurate, and "
    "clear about what you can and cannot do. Never claim internet access or "
    "system changes unless they actually occurred."
)


def installed_models():
    if not MODEL_DIR.exists():
        return []
    return [p.name for p in MODEL_DIR.iterdir() if p.is_file() and p.suffix.lower() == ".gguf"]


def ollama_chat(message):
    model = MODEL or os.environ.get("COPPER_OLLAMA_MODEL", "")
    if not model:
        return None
    payload = json.dumps({
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
    }).encode()
    req = urllib.request.Request(
        OLLAMA_URL.rstrip("/") + "/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.load(response)
        return data.get("message", {}).get("content")
    except Exception:
        return None


class Handler(BaseHTTPRequestHandler):
    def _json(self, status, data):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"ok": True, "models": installed_models(), "model": MODEL})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/chat":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
            message = str(body.get("message", "")).strip()
            if not message:
                raise ValueError("message is required")
        except (ValueError, json.JSONDecodeError):
            self._json(400, {"error": "invalid request"})
            return

        answer = ollama_chat(message)
        if answer is None:
            answer = (
                "Merhaba! Ben Copper. Şu anda yerel bir model bağlı değil. "
                "Bir GGUF modelini /opt/copperbars/models/ klasörüne ekleyebilir "
                "veya yerel Ollama modelini COPPER_OLLAMA_MODEL ile seçebilirsin."
            )
        self._json(200, {"answer": answer, "local": True})

    def log_message(self, *_):
        return


if __name__ == "__main__":
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
