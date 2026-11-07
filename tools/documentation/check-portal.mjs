// Inspección automatizada del HTML generado, aislada de cuentas y bases del producto.
import { createServer } from 'node:http';
import { readFile, readdir, mkdir, writeFile, copyFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const root = fileURLToPath(new URL('../../', import.meta.url));
const site = path.join(root, 'quarto/_site');
const evidence = path.join(root, 'docs/evaluacion/entrega-final/evidencias-automaticas');
await mkdir(evidence, { recursive: true });
const mime = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.json': 'application/json', '.woff2': 'font/woff2' };
const server = createServer(async (req, res) => {
  try {
    let requested = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (requested.endsWith('/')) requested += 'index.html';
    const target = path.resolve(site, `.${requested}`);
    if (!target.startsWith(site + path.sep)) throw new Error('Invalid path');
    const data = await readFile(target);
    res.writeHead(200, { 'Content-Type': `${mime[path.extname(target)] || 'application/octet-stream'}; charset=utf-8` });
    res.end(data);
  } catch {
    res.writeHead(404); res.end('Not found');
  }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch({ headless: true });
const failures = [];
let checked = 0;
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.on('pageerror', error => failures.push(error.message));
  const files = (await readdir(site, { recursive: true })).filter(name => name.endsWith('.html')).sort();
  for (const file of files) {
    const response = await page.goto(`${base}/${file.replaceAll(path.sep, '/')}`, { waitUntil: 'networkidle' });
    if (!response.ok()) throw new Error(`HTTP ${response.status()}: ${file}`);
    await page.evaluate(() => document.fonts.ready);
    const problems = await page.evaluate(() => ({
      images: [...document.querySelectorAll('img')].filter(img => !img.complete || !img.naturalWidth).map(img => img.getAttribute('src')),
      mermaid: [...document.querySelectorAll('.mermaid')].filter(node => /Syntax error|Parse error|UnknownDiagramError/.test(node.textContent)).length,
      heading: Boolean(document.querySelector('h1')),
    }));
    if (problems.images.length || problems.mermaid || !problems.heading) failures.push(`${file}: ${JSON.stringify(problems)}`);
    checked++;
    console.log(`HTML Chromium OK: ${file}`);
  }
  await page.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(evidence, 'portal-escritorio.png'), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload({ waitUntil: 'networkidle' });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 2);
  if (overflow) failures.push('Inicio móvil: desbordamiento horizontal de página');
  await page.screenshot({ path: path.join(evidence, 'portal-movil.png'), fullPage: true });
  await page.setViewportSize({ width: 1900, height: 1100 });
  const diagramFiles = (await readdir(path.join(site, 'diagrams'))).filter(name => name.endsWith('.svg'));
  if (diagramFiles.length !== 8) failures.push(`Se esperaban ocho SVG; hay ${diagramFiles.length}`);
  for (const svg of diagramFiles.sort()) {
    const name = svg === 'bpmn-Diagram_Create.svg' ? 'bpmn-creacion.png' : svg === 'C4-Codigo.svg' ? 'uml-codigo.png' : svg.replace(/\.svg$/, '.png');
    await page.setContent(`<!doctype html><html><body style="margin:0;background:white"><img alt="Modelo formal renderizado" src="${base}/diagrams/${svg}"></body></html>`);
    await page.locator('img').evaluate(img => img.decode());
    await page.locator('img').screenshot({ path: path.join(evidence, name) });
  }
  const result = { kind: 'inspeccion automatizada de documentacion local, no demostracion humana del producto', generated_at: new Date().toISOString(), browser: browser.version(), pages: checked, diagrams: diagramFiles.length, viewports: ['1440x1000', '390x844'], failures };
  await writeFile(path.join(evidence, 'resultado-portal.json'), JSON.stringify(result, null, 2) + '\n', 'utf8');
  if (failures.length) throw new Error(failures.join('\n'));
  // Incorporar las capturas de esta ejecución al artefacto publicado, sin otro render.
  const publishedEvidence = path.join(site, 'sources/docs/evaluacion/entrega-final/evidencias-automaticas');
  await mkdir(publishedEvidence, { recursive: true });
  for (const name of (await readdir(evidence)).filter(name => /\.(png|json)$/.test(name))) {
    await copyFile(path.join(evidence, name), path.join(publishedEvidence, name));
  }
  console.log(`Chromium: ${checked} páginas, imágenes y Mermaid sin errores; inicio escritorio/móvil OK.`);
} finally {
  await browser.close();
  await new Promise(resolve => server.close(resolve));
}
