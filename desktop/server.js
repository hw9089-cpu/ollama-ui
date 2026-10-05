// 內建的輕量伺服器：提供 index.html，並把 /api/* 串流轉發到 Ollama（等同 serve.py）
const http = require('http');
const fs = require('fs');

function start({ indexPath, ollama }) {
  const target = new URL(/^https?:\/\//.test(ollama) ? ollama : 'http://' + ollama);
  const server = http.createServer((req, res) => {
    if (req.url.startsWith('/api/')) {
      const up = http.request({
        hostname: target.hostname, port: target.port || 80, path: req.url, method: req.method,
        headers: { 'Content-Type': 'application/json', ...(req.headers['content-length'] ? { 'Content-Length': req.headers['content-length'] } : {}) },
      }, r => {
        res.writeHead(r.statusCode, { 'Content-Type': r.headers['content-type'] || 'application/json' });
        r.pipe(res);
      });
      up.on('error', e => {
        if (!res.headersSent) res.writeHead(502, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end(`無法連線 Ollama (${target.host}): ${e.message}`);
      });
      res.on('close', () => up.destroy()); // 使用者按停止
      req.pipe(up);
    } else if (req.url === '/' || req.url === '/index.html') {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      fs.createReadStream(indexPath).pipe(res);
    } else {
      res.writeHead(404); res.end();
    }
  });
  return new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve({ server, port: server.address().port })));
}
module.exports = { start };
