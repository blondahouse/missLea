"""Deterministic OpenAI-compatible mock. Never calls a real model or network API.

Start one process per tier, e.g.
python -m router_lab.mock_provider --tier primary --port 19100
"""
from __future__ import annotations

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class LabServer(ThreadingHTTPServer):
    def __init__(self, address, handler, tier):
        super().__init__(address, handler)
        self.tier = tier
        self.events = []
        self.lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    server: LabServer

    def log_message(self, fmt, *args):
        return  # Synthetic labels only; never log request bodies or auth headers.

    def reply(self, status, obj):
        raw = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/health":
            return self.reply(200, {"ok": True, "tier": self.server.tier})
        if self.path in ("/v1/models", "/models"):
            return self.reply(200, {
                "object": "list",
                "data": [{"id": name, "object": "model", "owned_by": "lab"}
                         for name in ("lab-model", "lab-embed")],
            })
        if self.path == "/lab/events":
            with self.server.lock:
                events = list(self.server.events)
            return self.reply(200, {"tier": self.server.tier, "events": events})
        return self.reply(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/lab/reset":
            with self.server.lock:
                self.server.events.clear()
            return self.reply(200, {"ok": True})
        if self.path not in ("/v1/chat/completions", "/chat/completions",
                             "/v1/embeddings", "/embeddings"):
            return self.reply(404, {"error": "not_found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 65536 or length < 2:
                return self.reply(413, {"error": "invalid_body"})
            body = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            return self.reply(400, {"error": "invalid_json"})
        messages = body.get("messages", [])
        prompt = " ".join(
            str(m.get("content", "")) for m in messages if isinstance(m, dict)
        )
        marker = next((m for m in ("LAB_BASIC", "LAB_QUOTA", "LAB_OUTAGE",
                                   "LAB_TOOL", "LAB_STREAM", "LAB_EMBED")
                       if m in prompt), "LAB_OTHER")
        tier = self.server.tier
        if marker == "LAB_QUOTA" and tier == "primary":
            status = 429
        elif marker == "LAB_OUTAGE" and tier != "paid":
            status = 503
        else:
            status = 200
        with self.server.lock:
            self.server.events.append({
                "tier": tier, "scenario": marker, "status": status,
                "endpoint": "embeddings" if "embeddings" in self.path else "chat",
            })
        if status != 200:
            return self.reply(status, {
                "error": {
                    "message": "synthetic failure",
                    "type": "rate_limit_error" if status == 429 else "service_unavailable",
                    "code": "rate_limit_exceeded" if status == 429 else "service_unavailable",
                }
            })
        model = body.get("model", "lab-model")
        if "embeddings" in self.path:
            return self.reply(200, {
                "object": "list", "model": model,
                "data": [{"object": "embedding", "index": 0,
                          "embedding": [0.1, 0.2, 0.3]}],
                "usage": {"prompt_tokens": 4, "total_tokens": 4},
            })
        if marker == "LAB_TOOL" and body.get("tools"):
            msg = {
                "role": "assistant", "content": None,
                "tool_calls": [{
                    "id": "call_lab", "type": "function",
                    "function": {"name": "inspect", "arguments": '{"ok":true}'},
                }],
            }
            finish = "tool_calls"
        else:
            msg = {"role": "assistant", "content": "mock:" + tier}
            finish = "stop"
        response = {
            "id": "chatcmpl-lab", "object": "chat.completion",
            "created": 1735689600, "model": model,
            "choices": [{"index": 0, "message": msg, "finish_reason": finish}],
            "usage": {"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6},
        }
        if body.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            chunk = {
                "id": "chatcmpl-lab", "object": "chat.completion.chunk",
                "created": 1735689600, "model": model,
                "choices": [{"index": 0, "delta": {
                    "role": "assistant", "content": "mock:" + tier
                }, "finish_reason": None}],
            }
            self.wfile.write(("data: " + json.dumps(chunk) + "\n\n").encode())
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            return
        self.reply(200, response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", choices=["primary", "backup", "paid"], required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    server = LabServer(("127.0.0.1", args.port), Handler, args.tier)
    try:
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
