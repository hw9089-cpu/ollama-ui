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
import platform
import sys
import time
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


def is_local(target):
    return target.split(":")[0] in ("127.0.0.1", "localhost", "::1", "0.0.0.0")


def local_sys():
    """本機 CPU / 記憶體 / 磁碟。優先 psutil，否則退回 /proc（Linux）。"""
    info = {"host": platform.node(), "os": f"{platform.system()} {platform.release()}"}
    try:
        import psutil
        vm = psutil.virtual_memory()
        info.update(cpu=psutil.cpu_percent(interval=0.3), cores=psutil.cpu_count(),
                    mem_used=vm.total - vm.available, mem_total=vm.total,
                    disk=psutil.disk_usage(os.path.expanduser("~")).percent)
        try:
            t = psutil.sensors_temperatures()
            for k in ("coretemp", "k10temp", "cpu_thermal"):
                if k in t and t[k]:
                    info["temp"] = t[k][0].current
                    break
        except Exception:
            pass
        return info
    except ImportError:
        pass
    try:  # Linux 後備
        mem = {l.split(":")[0]: int(l.split()[1]) * 1024 for l in open("/proc/meminfo")}

        def cpu_times():
            v = list(map(int, open("/proc/stat").readline().split()[1:]))
            return sum(v), v[3] + v[4]
        t1, i1 = cpu_times(); time.sleep(0.3); t2, i2 = cpu_times()
        info.update(cpu=round(100 * (1 - (i2 - i1) / max(1, t2 - t1)), 1), cores=os.cpu_count(),
                    mem_total=mem["MemTotal"], mem_used=mem["MemTotal"] - mem["MemAvailable"])
    except Exception as e:
        info["error"] = str(e)
    return info


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"  # 以連線關閉結束串流，最簡單

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self.proxy()
        if self.path == "/__config":
            return self.json({"target": state["target"]})
        if self.path == "/__sys":
            # 目標是遠端 serve.py 時，向它要「那台機器」的資源；目標是本機 Ollama 時就取本機
            target = state["target"]
            if is_local(target):
                return self.json(local_sys())
            try:
                c = http.client.HTTPConnection(target, timeout=4)
                c.request("GET", "/__sys")
                r = c.getresponse()
                if r.status == 200:
                    return self.json(json.loads(r.read()))
            except Exception:
                pass
            return self.json({"error": "遠端沒有提供系統資訊（請在 Ollama 那台機器執行 serve.py）"})
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
        if self.path.startswith("/__save"):
            # 匯出檔案到 ~/Downloads/ollama-ui/（桌面版沒有瀏覽器下載功能時使用），只允許本機
            if self.client_address[0] not in ("127.0.0.1", "::1"):
                return self.send_error(403)
            from urllib.parse import parse_qs, urlparse
            name = os.path.basename(parse_qs(urlparse(self.path).query).get("name", ["export.txt"])[0]) or "export.txt"
            length = int(self.headers.get("Content-Length") or 0)
            folder = os.path.join(os.path.expanduser("~"), "Downloads", "ollama-ui")
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, name)
            with open(path, "wb") as f:
                f.write(self.rfile.read(length))
            return self.json({"path": path})
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
