#!/usr/bin/env python3
"""在 Mac 上執行:  python3 serve.py
提供 index.html，並把 /api/* 串流轉發到本機 Ollama（避免 CORS 問題）。
環境變數:
  OLLAMA_HOST  預設 127.0.0.1:11434
  PORT         預設 8080
  BIND         預設 127.0.0.1（要讓區網其他裝置使用請設 0.0.0.0）
"""
import http.client
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

OLLAMA = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434").replace("http://", "")
PORT = int(os.environ.get("PORT", "8080"))
BIND = os.environ.get("BIND", "127.0.0.1")
HERE = os.path.dirname(os.path.abspath(__file__))


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"  # 以連線關閉結束串流，最簡單

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self.proxy()
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
        self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            return self.proxy()
        self.send_error(404)

    def proxy(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        try:
            conn = http.client.HTTPConnection(OLLAMA, timeout=600)
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
                self.send_error(502, f"無法連線 Ollama ({OLLAMA}): {e}")
            except Exception:
                pass

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print(f"Ollama UI:  http://{'localhost' if BIND == '127.0.0.1' else BIND}:{PORT}   (Ollama -> {OLLAMA})")
    ThreadingHTTPServer((BIND, PORT), Handler).serve_forever()
