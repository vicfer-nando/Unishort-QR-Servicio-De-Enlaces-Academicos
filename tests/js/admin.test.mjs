// JavaScript real y DOM/red simulados. No depende de la red ni de paquetes npm.
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { mountAdmin } from '../../frontend/admin.mjs';

class Element {
  constructor(tag = 'div') { this.tagName = tag; this.value = ''; this.textContent = ''; this.children = []; this.listeners = {}; this.hidden = false; this.disabled = false; this.checked = false; this.dataset = {}; }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  async fire(name, data = {}) { return this.listeners[name]?.({ preventDefault() {}, ...data }); }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(name, value) { this[name] = value; }
  focus() { this.focused = true; }
  showModal() { this.open = true; }
  close() { this.open = false; }
  remove() {}
  click() { return this.fire('click'); }
}

const link = { short_code: 'abc2345', short_url: 'http://localhost:8000/s/abc2345', original_url: 'https://example.edu/<img onerror=alert(1)>', status: 'active', is_active: true, click_count: 4, expires_at: null, created_at: '2026-01-01T00:00:00Z' };
const summary = { total_links: 1, active_links: 1, inactive_links: 0, expired_links: 0, total_visits: 4 };
function fixture() {
  const elements = new Map();
  const byId = id => { if (!elements.has(id)) elements.set(id, new Element()); return elements.get(id); };
  byId('page-size').value = '20'; byId('language').value = 'es';
  const requests = [], downloads = [], revoked = [], copied = [];
  const listeners = {};
  const state = { status: 200, items: [structuredClone(link)], total: 1, response: null };
  const doc = { getElementById: byId, querySelectorAll: () => [], createElement: tag => {
    const element = new Element(tag);
    if (tag === 'a') element.click = () => downloads.push({ href: element.href, download: element.download });
    return element;
  }, documentElement: {}, body: new Element() };
  class BlobURL extends URL {
    static createObjectURL() { return 'blob:qr'; }
    static revokeObjectURL(url) { revoked.push(url); }
  }
  const win = { location: { href: 'http://localhost:5500/admin.html' }, addEventListener(name, fn) { listeners[name] = fn; } };
  const app = mountAdmin({ document: doc, window: win, URL: BlobURL, navigator: { clipboard: { async writeText(value) { copied.push(value); } } }, fetch: async (url, options) => {
    requests.push({ url, options });
    if (state.response) return state.response(url, options);
    return { ok: state.status === 200, status: state.status, headers: { get: () => url.endsWith('/qr') ? 'image/png' : 'application/json' },
      json: async () => ({ success: state.status === 200, data: url.includes('/admin/stats') ? summary : { items: state.items, total: state.total, limit: 20, offset: 0 } }), blob: async () => ({ type: 'image/png' }) };
  } });
  const login = async () => { byId('admin-key').value = 'transient-secret'; await byId('login-form').fire('submit'); };
  return { app, byId, requests, state, login, downloads, revoked, copied, listeners };
}

function buttons(row) { return row.children.at(-1).children; }

test('sin autenticación no hay solicitudes; ingreso valida clave solo por cabecera', async () => {
  const f = fixture();
  await f.byId('refresh').fire('click');
  await f.byId('filters').fire('submit');
  assert.equal(f.requests.length, 0);
  await f.login();
  assert.ok(f.requests[0].url.endsWith('/api/v1/links?limit=20&offset=0'));
  for (const request of f.requests) {
    assert.equal(request.options.headers['X-Admin-API-Key'], 'transient-secret');
    assert.equal(request.options.cache, 'no-store');
    assert.equal(request.options.credentials, 'omit');
    assert.equal(request.options.redirect, 'error');
    assert.ok(!request.url.includes('transient-secret'));
  }
  assert.equal(f.byId('admin-key').value, '');
  assert.equal(f.byId('dashboard').hidden, false);
  assert.equal(f.byId('metric-total_links').textContent, '1');
});

for (const [status, pattern] of [[401, /clave/i], [403, /incorrecta/i], [503, /configurada/i]]) {
  test(`login ${status} informa error y borra clave`, async () => {
    const f = fixture(); f.state.status = status; await f.login();
    assert.match(f.byId('feedback').textContent, pattern);
    assert.ok(!f.byId('feedback').textContent.includes('transient-secret'));
    assert.equal(f.byId('dashboard').hidden, true);
    assert.equal(f.byId('admin-key').value, '');
    const count = f.requests.length; await f.byId('refresh').fire('click');
    assert.equal(f.requests.length, count);
  });
}

test('búsqueda/filtros/paginación en servidor y estado vacío', async () => {
  const f = fixture(); await f.login(); f.state.total = 42;
  f.byId('query').value = '100%_<script>'; f.byId('status-filter').value = 'inactive';
  await f.byId('filters').fire('submit');
  let url = new URL(f.requests.at(-1).url);
  assert.equal(url.searchParams.get('q'), '100%_<script>');
  assert.equal(url.searchParams.get('status'), 'inactive');
  await f.byId('next').fire('click');
  url = new URL(f.requests.at(-1).url); assert.equal(url.searchParams.get('offset'), '20');
  await f.byId('previous').fire('click');
  assert.equal(new URL(f.requests.at(-1).url).searchParams.get('offset'), '0');
  f.state.items = []; f.state.total = 0; await f.byId('refresh').fire('click');
  assert.equal(f.byId('empty').hidden, false);
  assert.equal(f.byId('next').disabled, true);
});

test('URL no confiable se muestra como texto; copiar, abrir y descargar QR sin clave', async () => {
  const f = fixture(); await f.login();
  const row = f.byId('link-rows').children[0];
  assert.equal(row.children[0].children[1].textContent, link.original_url);
  const [copy, open, qr] = buttons(row);
  assert.equal(open.href, link.short_url); assert.equal(open.rel, 'noopener noreferrer');
  await copy.click(); assert.deepEqual(f.copied, [link.short_url]);
  await qr.click();
  assert.equal(f.requests.at(-1).options.headers['X-Admin-API-Key'], undefined);
  assert.equal(f.downloads[0].download, 'unishort-abc2345.png');
  assert.deepEqual(f.revoked, ['blob:qr']);
});

test('gestión requiere confirmar; valida fecha, conserva PATCH y permite quitar caducidad', async () => {
  const f = fixture(); await f.login();
  await buttons(f.byId('link-rows').children[0])[3].click();
  assert.equal(f.byId('edit-dialog').open, true);
  assert.equal(f.requests.filter(r => r.options.method === 'PATCH').length, 0);
  f.byId('edit-expiration').value = '2000-01-01T00:00';
  await f.byId('edit-form').fire('submit');
  assert.equal(f.requests.filter(r => r.options.method === 'PATCH').length, 0);
  f.byId('edit-expiration').value = ''; f.byId('edit-active').checked = false;
  await f.byId('edit-form').fire('submit');
  const patch = f.requests.find(r => r.options.method === 'PATCH');
  assert.deepEqual(JSON.parse(patch.options.body), { is_active: false });
  assert.equal(f.byId('edit-dialog').open, false);
});

test('reactivar, cambiar fecha futura y eliminar fecha usan el contrato existente', async () => {
  const f = fixture(); f.state.items[0] = { ...link, is_active: false, status: 'inactive', expires_at: '2000-01-01T00:00:00Z' }; await f.login();
  await buttons(f.byId('link-rows').children[0])[3].click();
  f.byId('edit-active').checked = true; f.byId('edit-expiration').value = '';
  await f.byId('edit-form').fire('submit');
  assert.deepEqual(JSON.parse(f.requests.find(r => r.options.method === 'PATCH').options.body), { is_active: true, expires_at: null });
  await buttons(f.byId('link-rows').children[0])[3].click();
  f.byId('edit-expiration').value = '2099-01-01T12:30';
  await f.byId('edit-form').fire('submit');
  assert.ok(JSON.parse(f.requests.filter(r => r.options.method === 'PATCH').at(-1).options.body).expires_at.endsWith('Z'));
});

test('cerrar sesión cancela solicitudes y descarta respuestas tardías', async () => {
  const f = fixture(); await f.login(); let resolve;
  f.state.response = () => new Promise(done => { resolve = done; });
  const refresh = f.byId('refresh').fire('click');
  await f.byId('logout').fire('click');
  assert.equal(f.requests.at(-1).options.signal.aborted, true);
  resolve({ ok: true, status: 200, json: async () => ({ success: true, data: summary }) });
  await refresh;
  assert.equal(f.byId('dashboard').hidden, true);
  assert.equal(f.byId('link-rows').children.length, 0);
  const count = f.requests.length; await f.byId('refresh').fire('click');
  assert.equal(f.requests.length, count);
});

test('fallo de red, 500 y 401 durante sesión no filtran errores ni credenciales', async () => {
  const f = fixture(); await f.login();
  f.state.response = async () => { throw new Error('transient-secret arbitrary server text'); };
  await f.byId('refresh').fire('click');
  assert.match(f.byId('feedback').textContent, /conectar/i);
  assert.ok(!f.byId('feedback').textContent.includes('transient-secret'));
  f.state.response = null; f.state.status = 500;
  await f.byId('refresh').fire('click'); assert.match(f.byId('feedback').textContent, /servidor/i);
  f.state.status = 401; await f.byId('refresh').fire('click');
  assert.equal(f.byId('dashboard').hidden, true);
});

test('esquemas peligrosos no crean enlaces y QR inactivo queda deshabilitado', async () => {
  const f = fixture(); f.state.items[0] = { ...link, short_url: 'javascript:alert(1)', status: 'expired' };
  await f.login(); const actions = buttons(f.byId('link-rows').children[0]);
  assert.equal(actions[1].href, undefined);
  assert.equal(actions[2].disabled, true);
});

test('salir de página elimina sesión y el código no persiste credenciales', async () => {
  const f = fixture(); await f.login(); f.listeners.pagehide();
  assert.equal(f.byId('dashboard').hidden, true);
  const source = readFileSync(new URL('../../frontend/admin.mjs', import.meta.url), 'utf8');
  assert.doesNotMatch(source, /localStorage|sessionStorage|document\.cookie|innerHTML|console\./);
});

test('respuesta de login tardía no abre panel después de abandonar la página', async () => {
  const f = fixture(); let resolve;
  f.state.response = () => new Promise(done => { resolve = done; });
  const login = f.login(); f.listeners.pagehide();
  resolve({ ok: true, status: 200, json: async () => ({ success: true, data: summary }) });
  await login; assert.equal(f.byId('dashboard').hidden, true);
  assert.equal(f.requests.length, 1);
});

test('cancelar gestión no modifica datos y cambiar idioma no envía la clave', async () => {
  const f = fixture(); await f.login();
  await buttons(f.byId('link-rows').children[0])[3].click();
  await f.byId('edit-cancel').click(); assert.equal(f.byId('edit-dialog').open, false);
  assert.equal(f.requests.filter(r => r.options.method === 'PATCH').length, 0);
  const count = f.requests.length; f.byId('language').value = 'en'; await f.byId('language').fire('change');
  assert.equal(buttons(f.byId('link-rows').children[0])[3].textContent, 'Manage');
  assert.equal(f.requests.length, count);
});

for (const [status, pattern] of [[404, /disponible/i], [410, /caducado/i], [422, /fecha/i], [429, /solicitudes/i]]) {
  test(`PATCH ${status} mantiene diálogo y muestra error sin texto del servidor`, async () => {
    const f = fixture(); await f.login(); await buttons(f.byId('link-rows').children[0])[3].click();
    f.byId('edit-active').checked = false; f.state.status = status; await f.byId('edit-form').fire('submit');
    assert.equal(f.byId('edit-dialog').open, true); assert.match(f.byId('edit-feedback').textContent, pattern);
  });
}

test('rechaza JSON malformado y descargas QR con tipo incorrecto', async () => {
  const f = fixture(); await f.login();
  f.state.response = async () => ({ ok: true, status: 200, headers: { get: () => 'text/html' } });
  await buttons(f.byId('link-rows').children[0])[2].click();
  assert.equal(f.downloads.length, 0); assert.match(f.byId('feedback').textContent, /no válida/i);
  f.state.response = async () => ({ ok: true, status: 200, json: async () => ({ success: false, message: 'transient-secret' }) });
  await f.byId('refresh').click(); assert.match(f.byId('feedback').textContent, /no válida/i);
  assert.ok(!f.byId('feedback').textContent.includes('transient-secret'));
});
