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
