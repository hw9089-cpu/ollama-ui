# Ollama 本地 AI 對話 UI

同一份介面 (`index.html`)，兩種用法：網頁版、桌面版。

## 功能
- **對話**：串流輸出、Markdown/程式碼區塊、思考過程（Qwen3 等）、重新生成、編輯上一則、複製、搜尋與重新命名對話、圖片輸入（視覺模型自動出現 📎）、`Ctrl+K` 新對話、`Esc` 停止
- **即時監控**：生成速度 / 上下文儀表、首字延遲與速度紀錄、**主機 CPU／記憶體／磁碟／溫度**、已載入模型與 VRAM、卸載模型、即時日誌
- **設定**：Ollama 位址、系統提示詞、temperature、top_p、num_ctx、最大輸出、keep_alive、思考模式開關
- **模型管理**：下載（含進度）、刪除
- **資料**：匯出 .md / .json、匯入 .json

## 網頁版（在跑 Ollama 的機器上）
```bash
python3 serve.py                # http://localhost:8080
BIND=0.0.0.0 python3 serve.py   # 讓區網 / Tailscale 其他裝置連線
bash install-service.sh         # 開機自動啟動（Linux systemd / macOS launchd）
```
> 開放 `0.0.0.0` 後，同網路的人都能使用你的 Ollama，請只在信任的網路（如 Tailscale）使用。

## 桌面版（Windows / macOS / Linux）
```bash
pip install -r requirements-desktop.txt   # 想看本機 CPU/記憶體再加裝 psutil
python app.py
```
打包：`pyinstaller --noconfirm --windowed --name OllamaUI --add-data "index.html;." app.py`（macOS/Linux 把 `;` 換成 `:`），輸出在 `dist/`。

## 設定 Ollama 位址
設定頁的「Ollama 位址」填 `主機:埠`，存到 `~/.ollama-ui.json`。
- Ollama 在本機：`127.0.0.1:11434`（預設）
- Ollama 在另一台機器：填那台 `serve.py` 的位址（如 `100.x.x.x:8080`），不必改 Ollama 的監聽設定，主機資源也會顯示那台機器的數據。
