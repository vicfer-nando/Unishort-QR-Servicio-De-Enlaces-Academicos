// Ejecuta el JavaScript real con DOM y fetch simulados; no sustituye un navegador.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const html = readFileSync(new URL('../frontend/index.html', import.meta.url), 'utf8');
const source = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];
const elements = new Map();
const downloads = [];
const requests = [];
const revoked = [];
let mode = 'success';
const element = id => {
  if (!elements.has(id)) elements.set(id, {
    value: '', textContent: '', style: {}, disabled: false,
    classList: { add() {}, remove() {} },
    listeners: {}, addEventListener(event, callback) { this.listeners[event] = callback; },
  });
  return elements.get(id);
};
class LocalURL extends URL {
  static createObjectURL(blob) { assert.equal(blob.type, 'image/png'); return 'blob:local-qr'; }
  static revokeObjectURL(url) { revoked.push(url); }
}
const data = {
  short_code: 'abc2345', short_url: 'http://localhost:8000/s/abc2345',
  original_url: 'https://example.edu', qr_url: 'http://localhost:8000/api/v1/links/abc2345/qr',
};
const context = vm.createContext({
  window: {}, URL: LocalURL,
  document: {
    getElementById: element,
    createElement: () => ({ click() { downloads.push({ href: this.href, filename: this.download }); }, remove() {} }),
    body: { appendChild() {} },
  },
  setTimeout(callback) { callback(); },
  async fetch(url, options) {
    requests.push({ url, options });
    if (mode === 'network') throw new Error('Network failure');
    return {
      ok: mode !== 'error', status: mode === 'error' ? 400 : 200,
      headers: { get: () => 'application/json' },
      json: async () => mode === 'error' ? { errors: [{ message: 'URL rechazada' }] } : { success: true, data },
      blob: async () => ({ type: 'image/png' }),
    };
  },
});
vm.runInContext(source, context);
await context.shortenUrl();
assert.equal(requests.length, 0);
element('urlInput').value = 'invalid';
await context.shortenUrl();
assert.equal(requests.length, 0);
element('urlInput').value = 'https://example.edu';
await context.shortenUrl();
assert.equal(requests[0].url, 'http://localhost:8000/api/v1/links');
assert.equal(element('shortUrl').textContent, data.short_url);
assert.equal(element('qrImage').src, data.qr_url);
let prevented = false;
await element('qrDownload').listeners.click({
  preventDefault() { prevented = true; }, currentTarget: element('qrDownload'),
});
assert.ok(prevented);
assert.equal(downloads[0].href, 'blob:local-qr');
assert.equal(downloads[0].filename, 'unishort-abc2345.png');
assert.deepEqual(revoked, ['blob:local-qr']);
mode = 'error';
await context.shortenUrl();
assert.equal(element('message').textContent, 'URL rechazada');
assert.equal(element('shortenBtn').disabled, false);
mode = 'network';
await context.shortenUrl();
assert.match(element('message').textContent, /No se pudo conectar/);
assert.equal(element('shortenBtn').disabled, false);
console.log('JavaScript real: validación, creación, imagen QR, descarga Blob y errores OK.');
