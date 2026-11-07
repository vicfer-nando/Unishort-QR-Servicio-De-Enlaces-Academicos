import { messages } from './admin-i18n.mjs';

// La clave existe únicamente dentro de esta instancia; nunca se exporta.
export function mountAdmin(env = globalThis) {
  const { document: doc, window: win, fetch: request, navigator: nav, URL: Url } = env;
  const el = id => doc.getElementById(id);
  const metrics = ['total_links', 'active_links', 'inactive_links', 'expired_links', 'total_visits'];
  const base = new Url(win.UNISHORT_API_BASE_URL || 'http://localhost:8000');
  if (!['http:', 'https:'].includes(base.protocol) || base.username || base.password) throw new Error('Invalid API origin');
  const api = `${base.href.replace(/\/+$/, '')}/api/v1`;
  let key = '', authenticated = false, epoch = 0, busy = false, offset = 0, total = 0;
  let language = 'es', query = '', status = '', limit = 20, items = [], stats = null, editing = null;
  let initialExpiration = '';
  const controllers = new Set();
  const t = (name, values = {}) => Object.entries(values).reduce((text, [k, v]) => text.replace(`{${k}}`, String(v)), messages[language][name] || name);

  function feedback(name, kind = 'info', target = 'feedback') {
    el(target).textContent = name ? t(name) : '';
    el(target).dataset.kind = kind;
  }

  function translate() {
    doc.documentElement.lang = language;
    doc.title = t('title');
    doc.querySelectorAll('[data-i18n]').forEach(node => { node.textContent = t(node.dataset.i18n); });
    doc.querySelectorAll('[data-i18n-placeholder]').forEach(node => { node.placeholder = t(node.dataset.i18nPlaceholder); });
  }

  function controls() {
    el('login-submit').disabled = busy;
    el('admin-key').disabled = busy;
    for (const id of ['refresh', 'query', 'status-filter', 'page-size', 'search-submit', 'edit-save']) el(id).disabled = busy;
    el('previous').disabled = busy || offset === 0;
    el('next').disabled = busy || offset + limit >= total;
    el('dashboard').setAttribute('aria-busy', String(busy));
    doc.querySelectorAll('[data-row-action]').forEach(node => { node.disabled = busy || node.dataset.unavailable === 'true'; });
  }

  function logout(announce = true) {
    key = ''; authenticated = false; epoch += 1;
    controllers.forEach(controller => controller.abort()); controllers.clear();
    busy = false; items = []; stats = null; editing = null; offset = 0; total = 0;
    el('admin-key').value = ''; el('link-rows').replaceChildren();
    el('query').value = ''; el('status-filter').value = ''; query = ''; status = '';
    el('edit-expiration').value = ''; el('edit-active').checked = false; el('edit-code').textContent = '';
    metrics.forEach(name => { el(`metric-${name}`).textContent = '—'; });
    el('edit-dialog').close(); el('dashboard').hidden = true; el('logout').hidden = true; el('login-panel').hidden = false;
    feedback(''); feedback('', 'info', 'edit-feedback'); controls();
    if (announce) { feedback('loggedOut', 'success'); el('admin-key').focus(); }
  }

  function apiError(httpStatus) {
    const name = [401, 403, 503, 422, 404, 410, 429].includes(httpStatus) ? `error${httpStatus}` : 'serverError';
    const error = new Error(name); error.status = httpStatus; return error;
  }

  async function fetchData(path, options = {}, admin = true) {
    if (!key || (admin && !path.startsWith('/'))) throw new Error('error401');
    const version = epoch, controller = new AbortController(); controllers.add(controller);
    try {
      const headers = { 'Accept-Language': language, ...options.headers };
      if (admin) headers['X-Admin-API-Key'] = key;
      const response = await request(`${api}${path}`, { ...options, headers, signal: controller.signal, cache: 'no-store', credentials: 'omit', redirect: 'error', referrerPolicy: 'no-referrer' });
      if (version !== epoch) throw new Error('stale');
      if (!response.ok) throw apiError(response.status);
      if (!admin) {
        if (!(response.headers.get('content-type') || '').startsWith('image/png')) throw new Error('invalidResponse');
        const blob = await response.blob();
        if (version !== epoch) throw new Error('stale');
        return blob;
      }
      const body = await response.json();
      if (version !== epoch) throw new Error('stale');
      if (body.success !== true || !body.data) throw new Error('invalidResponse');
      return body.data;
    } finally { controllers.delete(controller); }
  }

  async function perform(action, success = '') {
    if (!key || busy) return;
    const version = epoch; busy = true; controls(); feedback('loading');
    try {
      await action();
      if (version === epoch) feedback(success, 'success');
    } catch (error) {
      if (version !== epoch || error.name === 'AbortError') return;
      const name = Object.hasOwn(messages[language], error.message) ? error.message : 'networkError';
      if ([401, 403, 503].includes(error.status) || !authenticated) logout(false);
      feedback(name, 'error');
      if (el('edit-dialog').open) feedback(name, 'error', 'edit-feedback');
    } finally { if (version === epoch || !key) { busy = false; controls(); } }
  }

  function safeUrl(value) {
    try {
      const url = new Url(value);
      return ['http:', 'https:'].includes(url.protocol) && !url.username && !url.password ? url.href : null;
    } catch { return null; }
  }

  function node(tag, text = '', className = '') {
    const result = doc.createElement(tag); result.textContent = text;
    if (className) result.className = className;
    return result;
  }

  function linkNode(item, text) {
    const url = safeUrl(item.short_url);
    if (!url) return node('span', text);
    const anchor = node('a', text); anchor.href = url; anchor.target = '_blank'; anchor.rel = 'noopener noreferrer'; return anchor;
  }

  function button(name, handler, unavailable = false) {
    const result = node('button', t(name)); result.type = 'button';
    result.dataset.rowAction = ''; result.dataset.unavailable = String(unavailable); result.disabled = busy || unavailable;
    result.addEventListener('click', handler); return result;
  }

  function formatDate(value) {
    const date = new Date(value);
    return value && !Number.isNaN(date.getTime()) ? date.toLocaleString(language) : t('noExpiration');
  }

  async function copy(item) {
    const version = epoch, url = safeUrl(item.short_url);
    if (!authenticated || !url) return;
    try { await nav.clipboard.writeText(url); if (version === epoch) feedback('copied', 'success'); }
    catch { if (version === epoch) feedback('copyFailed', 'error'); }
  }

  async function download(item) {
    if (!authenticated || item.status !== 'active') return;
    await perform(async () => {
      const blob = await fetchData(`/links/${encodeURIComponent(item.short_code)}/qr`, {}, false);
      const objectUrl = Url.createObjectURL(blob), anchor = node('a');
      try { anchor.href = objectUrl; anchor.download = `unishort-${item.short_code}.png`; doc.body.append(anchor); anchor.click(); }
      finally { anchor.remove(); Url.revokeObjectURL(objectUrl); }
    }, 'downloaded');
  }

  function renderRow(item) {
    const row = node('tr'), destination = node('td');
    destination.append(linkNode(item, item.short_code), node('span', item.original_url, 'destination'), node('span', `${t('created')}: ${formatDate(item.created_at)}`, 'created'));
    const stateCell = node('td'); stateCell.append(node('span', t(item.status), `badge ${['active', 'inactive', 'expired'].includes(item.status) ? item.status : ''}`));
    const actionCell = node('td', '', 'row-actions'), open = linkNode(item, t('open')); open.className = 'action-link';
    actionCell.append(button('copy', () => copy(item)), open, button('qr', () => download(item), item.status !== 'active'), button('manage', () => openEditor(item)));
    row.append(destination, stateCell, node('td', String(item.click_count)), node('td', formatDate(item.expires_at)), actionCell);
    return row;
  }

  function render() {
    if (stats) metrics.forEach(name => { el(`metric-${name}`).textContent = String(stats[name]); });
    el('link-rows').replaceChildren(...items.map(renderRow));
    el('empty').hidden = items.length > 0;
    el('page-info').textContent = t('page', { from: items.length ? offset + 1 : 0, to: offset + items.length, total });
    controls();
  }

  async function loadList() {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (query) params.set('q', query);
    if (status) params.set('status', status);
    const data = await fetchData(`/links?${params}`);
    if (!Array.isArray(data.items) || !Number.isInteger(data.total)) throw new Error('invalidResponse');
    // Una modificación concurrente puede dejar la última página vacía.
    if (offset > 0 && offset >= data.total) { offset = Math.max(0, Math.floor((data.total - 1) / limit) * limit); return loadList(); }
    items = data.items; total = data.total; render();
  }

  async function refresh() {
    stats = await fetchData('/admin/stats');
    await loadList();
  }

  function localDate(value) {
    if (!value) return '';
    const date = new Date(value);
    return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  }

  function openEditor(item) {
    if (!authenticated || busy) return;
    editing = item; el('edit-code').textContent = item.short_code;
    el('edit-active').checked = item.is_active;
    initialExpiration = localDate(item.expires_at); el('edit-expiration').value = initialExpiration;
    feedback('', 'info', 'edit-feedback'); el('edit-dialog').showModal();
  }

  async function save(event) {
    event.preventDefault();
    if (!editing || !authenticated || busy) return;
    const payload = {}, value = el('edit-expiration').value;
    if (el('edit-active').checked !== editing.is_active) payload.is_active = el('edit-active').checked;
    if (value !== initialExpiration) {
      const date = value ? new Date(value) : null;
      if (date && (Number.isNaN(date.getTime()) || date.getTime() <= Date.now())) { feedback('invalidDate', 'error', 'edit-feedback'); return; }
      payload.expires_at = date ? date.toISOString() : null;
    }
    if (!Object.keys(payload).length) { feedback('noChanges', 'info', 'edit-feedback'); return; }
    await perform(async () => {
      await fetchData(`/links/${encodeURIComponent(editing.short_code)}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      el('edit-dialog').close(); editing = null;
      // Guardado y recarga tienen resultados independientes: no repetir un PATCH exitoso.
      feedback('updated', 'success');
      await refresh();
    }, 'updated');
  }

  el('login-form').addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || authenticated) return;
    key = el('admin-key').value; el('admin-key').value = '';
    if (!key) { feedback('required', 'error'); return; }
    await perform(async () => {
      // El listado protegido preexistente valida la clave y aporta la primera página.
      await loadList(); stats = await fetchData('/admin/stats'); authenticated = true;
      el('login-panel').hidden = true; el('dashboard').hidden = false; el('logout').hidden = false;
      render(); el('query').focus();
    });
  });
  el('logout').addEventListener('click', () => logout());
  el('refresh').addEventListener('click', () => authenticated && perform(refresh));
  el('filters').addEventListener('submit', event => {
    event.preventDefault(); if (!authenticated || busy) return;
    query = el('query').value.trim(); status = el('status-filter').value; limit = Number(el('page-size').value); offset = 0;
    return perform(loadList);
  });
  el('previous').addEventListener('click', () => { if (!authenticated || busy || offset === 0) return; offset = Math.max(0, offset - limit); return perform(loadList); });
  el('next').addEventListener('click', () => { if (!authenticated || busy || offset + limit >= total) return; offset += limit; return perform(loadList); });
  el('edit-form').addEventListener('submit', save);
  el('edit-cancel').addEventListener('click', () => { el('edit-dialog').close(); editing = null; });
  el('language').addEventListener('change', () => { language = el('language').value === 'en' ? 'en' : 'es'; translate(); feedback(''); render(); });
  win.addEventListener('pagehide', () => logout(false));
  translate(); logout(false);
  return Object.freeze({ destroy: () => logout(false) });
}

if (typeof document !== 'undefined') mountAdmin();
