# Ollama UI

零依賴的本地 AI 聊天介面：單檔前端 `index.html` + Python 標準庫代理 `serve.py`。

## 功能
- 串流輸出、模型選擇、多對話紀錄（存於瀏覽器 localStorage）
- Markdown／程式碼區塊複製、深色模式、思考過程（qwen3 等）顯示
- 重新生成、編輯已送出的訊息
- 附加圖片（視覺模型，如 llava、qwen2.5vl）與文字檔，支援貼上圖片
- 對話匯出／匯入（JSON）

## 執行
```sh
python3 serve.py                 # http://localhost:8080
BIND=0.0.0.0 python3 serve.py    # 讓區網／Tailscale 其他裝置連線
```
環境變數：`OLLAMA_HOST`（預設 127.0.0.1:11434）、`PORT`（8080）、`BIND`（127.0.0.1）。

## 開機自動啟動（macOS）
```sh
cp com.ollama-ui.plist ~/Library/LaunchAgents/
# 編輯檔內的路徑（預設 ~/ollama-ui）後：
launchctl load ~/Library/LaunchAgents/com.ollama-ui.plist
```
更新後重啟：`launchctl kickstart -k gui/$(id -u)/com.ollama-ui`

注意：`BIND=0.0.0.0` 沒有任何驗證，請只在 Tailscale／可信網路使用。

## 桌面版（Windows，Electron）
`desktop/` 內含 Electron 版本，共用根目錄同一份 `index.html`，內建代理（不需要 Python），網頁版不受影響。

**取得安裝檔**：GitHub → Actions → *Build Windows desktop app* → Run workflow，完成後在該次執行的 Artifacts 下載 `ollama-ui-windows`（安裝程式 `.exe` 與免安裝 portable `.exe`）。

**自行建置／開發**（需要 Node 20+）：
```sh
cd desktop && npm install
npm start          # 直接開視窗
npm run build      # 產生 dist/*.exe（在 Windows 上執行）
```

**設定 Ollama 位址**：預設連本機 `127.0.0.1:11434`。選單「檔案 → 設定 Ollama 位址」會開啟 `%APPDATA%\Ollama UI\config.json`，
改成例如 `{"ollama":"100.100.138.103:11434"}`，再選「重新啟動以套用設定」。也可用環境變數 `OLLAMA_HOST`。
（遠端的 Ollama 需要自己監聽非本機位址，例如設 `OLLAMA_HOST=0.0.0.0`。）
