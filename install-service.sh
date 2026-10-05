#!/usr/bin/env bash
# 在「跑 Ollama 的那台機器」上執行：  bash install-service.sh
# 讓 serve.py 開機自動啟動、當掉自動重啟，並開放給區網 / Tailscale 連線（BIND=0.0.0.0）。
# 解除安裝：  bash install-service.sh uninstall
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
PY="$(command -v python3)"
PORT="${PORT:-8080}"

if [[ "$(uname)" == "Darwin" ]]; then
  PLIST="$HOME/Library/LaunchAgents/com.ollama-ui.plist"
  if [[ "$1" == "uninstall" ]]; then launchctl unload "$PLIST" 2>/dev/null || true; rm -f "$PLIST"; echo "已移除"; exit 0; fi
  cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.ollama-ui</string>
  <key>ProgramArguments</key><array><string>$PY</string><string>$DIR/serve.py</string></array>
  <key>EnvironmentVariables</key><dict><key>BIND</key><string>0.0.0.0</string><key>PORT</key><string>$PORT</string></dict>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$DIR/serve.log</string><key>StandardErrorPath</key><string>$DIR/serve.log</string>
</dict></plist>
EOF
  launchctl unload "$PLIST" 2>/dev/null || true
  launchctl load "$PLIST"
else
  UNIT="$HOME/.config/systemd/user/ollama-ui.service"
  if [[ "$1" == "uninstall" ]]; then systemctl --user disable --now ollama-ui 2>/dev/null || true; rm -f "$UNIT"; echo "已移除"; exit 0; fi
  mkdir -p "$(dirname "$UNIT")"
  cat > "$UNIT" <<EOF
[Unit]
Description=Ollama UI (serve.py)
After=network-online.target

[Service]
Environment=BIND=0.0.0.0 PORT=$PORT
WorkingDirectory=$DIR
ExecStart=$PY $DIR/serve.py
Restart=always

[Install]
WantedBy=default.target
EOF
  systemctl --user daemon-reload
  systemctl --user enable --now ollama-ui
  loginctl enable-linger "$USER" 2>/dev/null || true   # 未登入也能在開機後啟動
fi
echo "完成：http://localhost:$PORT"
