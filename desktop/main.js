const { app, BrowserWindow, Menu, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const { start } = require('./server');

// 設定檔：%APPDATA%\Ollama UI\config.json   例如 {"ollama":"192.168.1.10:11434"}
const cfgPath = () => path.join(app.getPath('userData'), 'config.json');
function loadConfig() {
  let c = {};
  try { c = JSON.parse(fs.readFileSync(cfgPath(), 'utf8')); } catch {}
  if (!fs.existsSync(cfgPath())) {
    try { fs.mkdirSync(path.dirname(cfgPath()), { recursive: true }); fs.writeFileSync(cfgPath(), JSON.stringify({ ollama: '127.0.0.1:11434' }, null, 2)); } catch {}
  }
  return { ollama: process.env.OLLAMA_HOST || c.ollama || '127.0.0.1:11434' };
}

if (!app.requestSingleInstanceLock()) app.quit();

app.whenReady().then(async () => {
  const cfg = loadConfig();
  const { port } = await start({ indexPath: path.join(__dirname, 'index.html'), ollama: cfg.ollama });
  const win = new BrowserWindow({ width: 1100, height: 780, title: 'Ollama UI', autoHideMenuBar: false });
  win.loadURL(`http://127.0.0.1:${port}/`);
  win.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: 'deny' }; });
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    { label: '檔案', submenu: [
      { label: '設定 Ollama 位址（編輯設定檔）', click: () => shell.openPath(cfgPath()) },
      { label: '重新啟動以套用設定', click: () => { app.relaunch(); app.exit(); } },
      { type: 'separator' }, { role: 'quit', label: '結束' } ] },
    { label: '檢視', submenu: [{ role: 'reload', label: '重新載入' }, { role: 'toggleDevTools', label: '開發者工具' }, { role: 'togglefullscreen', label: '全螢幕' }, { role: 'zoomIn' }, { role: 'zoomOut' }, { role: 'resetZoom' }] },
    { label: '編輯', submenu: [{ role: 'undo' }, { role: 'redo' }, { type: 'separator' }, { role: 'cut' }, { role: 'copy' }, { role: 'paste' }, { role: 'selectAll' }] },
  ]));
});
app.on('window-all-closed', () => app.quit());
