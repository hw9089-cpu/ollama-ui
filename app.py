#!/usr/bin/env python3
"""桌面版:  python app.py
在原生視窗中顯示同一份 index.html，內建代理（不需另外啟動 serve.py）。
安裝:  pip install pywebview
"""
import threading
from http.server import ThreadingHTTPServer

import webview

from serve import Handler


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)  # 隨機空閒埠
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    webview.create_window("Ollama 本地 AI 對話", url, width=1100, height=760, min_size=(720, 480))
    webview.start()
    server.shutdown()


if __name__ == "__main__":
    main()
