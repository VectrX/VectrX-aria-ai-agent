"""Aria: local-first, authenticated AI operations assistant starter.

Python 3.11+, standard library only. Does not autonomously mutate systems.
"""
import hmac
import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SYSTEM_PROMPT = (
    "You are Aria, the VectrX business operations assistant. Address the owner as "
    "MAVRO when appropriate. Help with VectrX and Red Velvet planning and support. "
    "Do not claim an action was executed without verified tool evidence. "
    "Never expose credentials. No sexually explicit content. "
    "Do not take financial, publishing or destructive actions without explicit approval."
)


def generate_reply(message: str) -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    model = os.environ.get("ARIA_MODEL", "gpt-4.1-mini")
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        "max_tokens": 500,
    }).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    return data["choices"][0]["message"]["content"]


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"status": "ok", "service": "aria", "mode": "local"})
        return self._send(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/api/chat":
            return self._send(404, {"error": "not_found"})
        expected = os.environ.get("ARIA_ADMIN_TOKEN", "")
        header = self.headers.get("Authorization", "")
        if not expected or not hmac.compare_digest(header, f"Bearer {expected}"):
            return self._send(401, {"error": "unauthorized"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 8192:
                return self._send(413, {"error": "invalid_request_size"})
            payload = json.loads(self.rfile.read(length))
            message = payload.get("message")
            if not isinstance(message, str) or not 0 < len(message.strip()) <= 4000:
                return self._send(400, {"error": "invalid_message"})
            reply = generate_reply(message)
            return self._send(200, {"reply": reply})
        except (ValueError, json.JSONDecodeError, KeyError, IndexError, TypeError):
            return self._send(400, {"error": "invalid_request"})
        except (RuntimeError, urllib.error.URLError, TimeoutError):
            return self._send(503, {"error": "ai_provider_unavailable"})
        except Exception:
            return self._send(500, {"error": "internal_error"})

    def log_message(self, format, *args):
        # Avoid logging private chat text or credentials.
        pass


def main():
    host = "127.0.0.1"  # Never expose this starter directly to the Internet.
    port = int(os.environ.get("ARIA_PORT", "4312"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Aria listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
