// 打包前把根目錄的 index.html 複製進來，確保網頁版與桌面版共用同一份
const fs = require('fs'), path = require('path');
fs.copyFileSync(path.join(__dirname, '..', '..', 'index.html'), path.join(__dirname, '..', 'index.html'));
