# Ollama 本地 AI 對話 UI

同一份介面 (`index.html`)，兩種用法：網頁版、桌面版。零後端依賴（網頁版只需 Python 3）。

## 網頁版（在跑 Ollama 的機器上）
```bash
python3 serve.py            # http://localhost:8080
BIND=0.0.0.0 python3 serve.py   # 讓區網 / Tailscale 其他裝置連線
```

## 桌面版（Windows / macOS / Linux）
```bash
pip install -r requirements-desktop.txt
python app.py
```
打包成可執行檔：
```bash
pyinstaller --noconfirm --windowed --name OllamaUI --add-data "index.html:." app.py   # Windows 用 ";" 取代 ":"
```
輸出在 `dist/`（Windows 為 `OllamaUI.exe`，macOS 為 `OllamaUI.app`；需在對應系統上打包）。

## 設定 Ollama 位址
左下角「Ollama 位址」填 `主機:埠`，會存到 `~/.ollama-ui.json`。
- Ollama 在本機：`127.0.0.1:11434`（預設）
- Ollama 在另一台機器：填那台的 `serve.py` 位址（如 `100.x.x.x:8080`），不必改 Ollama 的監聽設定。
