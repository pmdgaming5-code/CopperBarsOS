#!/usr/bin/env python3
"""CopperBarsOS local AI gateway.

The gateway is intentionally backend-agnostic and stays on localhost.
It prefers a locally installed Ollama model and falls back honestly when
no local model is configured.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import pathlib
import urllib.request

HOST = "127.0.0.1"
PORT = int(os.environ.get("COPPER_PORT", "8765"))
MODEL_DIR = pathlib.Path(os.environ.get("COPPER_MODEL_DIR", "/opt/copperbars/models"))
MODEL_CONFIG = pathlib.Path("/var/lib/copperbars/model.conf")
OLLAMA_URL = os.environ.get("COPPER_OLLAMA_URL", "http://127.0.0.1:11434")

SYSTEM_PROMPT = (
    "You are Copper, the friendly local AI assistant built into CopperBarsOS. "
    "Speak Turkish when the user speaks Turkish. Be concise, accurate, and "
    "clear about what you can and cannot do. Never claim internet access or "
    "system changes unless they actually occurred."
)


def selected_model():
    configured = os.environ.get("COPPER_MODEL", "").strip()
    if configured:
        return configured
    try:
        value = MODEL_CONFIG.read_text(encoding="utf-8").strip()
        return value
    except OSError:
        return os.environ.get("COPPER_OLLAMA_MODEL", "").strip()


def installed_models():
    if not MODEL_DIR.exists():
        return []
    return sorted(
        p.name for p in MODEL_DIR.iterdir()
        if p.is_file() and p.suffix.lower() == ".gguf"
    )


def ollama_chat(message):
    model = selected_model()
    if not model:
        return None
    payload = json.dumps({
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
    }, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_URL.rstrip("/") + "/api/chat",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.load(response)
        return data.get("message", {}).get("content")
    except Exception:
        return None


class Handler(BaseHTTPRequestHandler):
    def _json(self, status, data):
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/health":
            model = selected_model()
            self._json(200, {
                "ok": True,
                "models": installed_models(),
                "model": model,
                "backend": "ollama" if model else "none",
                "local_only": True,
            })
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/chat":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 1024 * 1024:
                raise ValueError("invalid content length")
            body = json.loads(self.rfile.read(length) or b"{}")
            message = str(body.get("message", "")).strip()
            if not message:
                raise ValueError("message is required")
        except (ValueError, json.JSONDecodeError):
            self._json(400, {"error": "invalid request"})
            return

        answer = ollama_chat(message)
        if answer is None:
            if selected_model():
                answer = "Copper'a yerel model bağlı görünüyor ama model servisine şu anda ulaşılamıyor. Copper Center'dan AI durumunu kontrol et."
            else:
                answer = (
                    "Merhaba! Ben Copper. Henüz bir yerel AI modeli seçilmemiş. "
                    "İlk kurulum ekranından model seçebilir veya Copper Center'dan "
                    "yerel model yapılandırabilirsin."
                )
        self._json(200, {"answer": answer, "local": True, "model": selected_model()})

    def log_message(self, *_):
        return


if __name__ == "__main__":
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
