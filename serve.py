#!/usr/bin/env python3
"""網頁版:  python3 serve.py
提供 index.html，並把 /api/* 串流轉發到 Ollama（避免 CORS 問題）。
桌面版 (app.py) 也重用這裡的 Handler。
環境變數:
  OLLAMA_HOST  預設 127.0.0.1:11434（也可在網頁左下角設定，會存到 ~/.ollama-ui.json）
  PORT         預設 8080
  BIND         預設 127.0.0.1（要讓區網其他裝置使用請設 0.0.0.0）
"""
import http.client
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "8080"))
BIND = os.environ.get("BIND", "127.0.0.1")
CONFIG = os.path.join(os.path.expanduser("~"), ".ollama-ui.json")
# 打包成 exe 時資源在 sys._MEIPASS
HERE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def clean_target(t):
    t = (t or "").strip()
    for p in ("http://", "https://"):
        if t.startswith(p):
            t = t[len(p):]
    return t.split("/")[0]


def load_target():
    try:
        with open(CONFIG, encoding="utf-8") as f:
            t = clean_target(json.load(f).get("target"))
            if t:
                return t
    except Exception:
        pass
    return clean_target(os.environ.get("OLLAMA_HOST")) or "127.0.0.1:11434"


state = {"target": load_target()}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"  # 以連線關閉結束串流，最簡單

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self.proxy()
        if self.path == "/__config":
            return self.json({"target": state["target"]})
        if self.path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self.proxy()
        if self.path == "/__config":
            # 只允許本機修改目標，避免區網其他人把代理指向任意位址
            if self.client_address[0] not in ("127.0.0.1", "::1"):
                return self.send_error(403)
            length = int(self.headers.get("Content-Length") or 0)
            try:
                t = clean_target(json.loads(self.rfile.read(length)).get("target"))
            except Exception:
                return self.send_error(400)
            if t:
                state["target"] = t
                try:
                    with open(CONFIG, "w", encoding="utf-8") as f:
                        json.dump({"target": t}, f)
                except OSError:
                    pass
            return self.json({"target": state["target"]})
        self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            return self.proxy()
        self.send_error(404)

    def json(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def proxy(self):
        target = state["target"]
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        try:
            conn = http.client.HTTPConnection(target, timeout=600)
            conn.request(self.command, self.path, body=body,
                         headers={"Content-Type": "application/json"})
            resp = conn.getresponse()
            self.send_response(resp.status)
            self.send_header("Content-Type", resp.getheader("Content-Type", "application/json"))
            self.end_headers()
            while True:
                chunk = resp.read1(4096)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
            conn.close()
        except (BrokenPipeError, ConnectionResetError):
            pass  # 使用者按了停止
        except Exception as e:
            try:
                self.send_error(502, f"無法連線 Ollama ({target}): {e}")
            except Exception:
                pass

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print(f"Ollama UI:  http://{'localhost' if BIND == '127.0.0.1' else BIND}:{PORT}   (Ollama -> {state['target']})")
    ThreadingHTTPServer((BIND, PORT), Handler).serve_forever()
